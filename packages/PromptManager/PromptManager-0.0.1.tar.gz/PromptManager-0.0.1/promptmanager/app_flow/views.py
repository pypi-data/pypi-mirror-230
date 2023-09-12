import logging
import os
import time
import uuid
from pathlib import Path

from django.db.models import Q

from promptmanager.app_flow.models import Flow, Module
from promptmanager.app_prompt.models import Prompt
from promptmanager.app_common.constant import Constant
from promptmanager.app_common.database_util import DatabaseUtil
from promptmanager.app_common.enum_publish_type import PublishType
from promptmanager.app_common.http_request_util import HttpRequestUtil
from promptmanager.app_common.json_util import JsonUtil
from promptmanager.app_common.page_util import PageUtil
from promptmanager.app_common.result_maker import ResultMaker
from promptmanager.app_common.enum_source_type import SourceType
from promptmanager.exception import exception
from promptmanager.app_app import views as app_service
from promptmanager.runtime.common_util import PMCommonUtil, FileUtil
from promptmanager.runtime.enumeration.enum_flow_status import PMFlowStatus
from promptmanager.runtime.flow import PMFlow, PMFlowEdge, PMFlowTemplateNode, PMFlowScriptNode
from promptmanager.runtime.template import PMPromptTemplate
from promptmanager.app_prompt import views as prompt_service
from promptmanager.app_model import views as model_service

logger = logging.getLogger('root')


# Create your views here.
def check_flow_name(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    name = request.GET.get('name')

    exists = __check_name_exists(name)

    result = {
        "exists": exists
    }

    return ResultMaker.success(result)


def __check_name_exists(name):
    try:
        flow = Flow.objects.get(name=name)
    except Exception as e:
        flow = None

    if flow:
        exists = True
    else:
        exists = False
    return exists


def add_flow(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    id = uuid.uuid4()
    name = params.get('name')
    description = params.get('description', '')

    exists = __check_name_exists(name)
    if exists:
        raise exception.FLOW_NAME_EXISTS

    # 封装pm_flow
    pm_flow = PMFlow()
    flow_json = {
        "nodes": JsonUtil.object_to_dict(pm_flow.nodes),
        "edges": JsonUtil.object_to_dict(pm_flow.edges)
    }

    flow = Flow(id=id, name=name, description=description, config=JsonUtil.object_to_json(flow_json), model_ids='[]',
                source=SourceType.USER.value, create_time=time.time(), update_time=time.time(),
                user_id=Constant.default_user_id)

    flow.save()
    return ResultMaker.success(id)


def get_flow_list(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    # page
    page_num = request.GET.get('pageIndex', 1)
    page_size = request.GET.get('pageNum', 15)
    # order
    order_key = request.GET.get('orderKey')
    if not order_key:
        order_key = 'update_time'

    order_by = request.GET.get('orderBy')
    if not order_by:
        order_by = 'desc'
    # keywords
    keywords = request.GET.get('keyWords', None)

    if order_by == 'desc':
        order_key = '-' + order_key

    if keywords:
        query_result = Flow.objects.filter(name__contains=keywords).order_by(order_key)
    else:
        query_result = Flow.objects.all().order_by(order_key)

    page_result = PageUtil.get_page(page_num=page_num, page_size=page_size, result=query_result)

    return ResultMaker.success(page_result)


def copy_flow(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)
    source_id = params.get('source_id')
    target_id = uuid.uuid4()
    target_name = params.get('target_name')
    # target_description = params.get('target_description', '')

    exists = __check_name_exists(target_name)
    if exists:
        raise exception.FLOW_NAME_EXISTS

    try:
        flow = Flow.objects.get(id=source_id)
    except Exception as e:
        raise exception.FLOW_NOT_FOUND()

    flow.id = target_id
    flow.name = target_name
    # if target_description:
    #     flow.description = target_description
    flow.create_time = time.time()
    flow.update_time = time.time()

    #  replace nodes and edges id
    if flow.config:
        flow.config = __replace_nodes_edges_id(JsonUtil.json_to_dict(flow.config))

    flow.save()

    return ResultMaker.success(target_id)


def __replace_nodes_edges_id(config):
    nodes = config['nodes']
    edges = config['edges']
    node_id_dict = {}
    for node in nodes:
        old_node_id = node['id']
        new_node_id = str(uuid.uuid4())

        node_id_dict[old_node_id] = new_node_id
        node['id'] = new_node_id

    for edge in edges:
        flow_edge = PMFlowEdge(**edge)
        edge['source_node'] = node_id_dict[flow_edge.source_node]
        edge['target_node'] = node_id_dict[flow_edge.target_node]

    new_config = {
        "nodes": node,
        "edges": edges
    }

    return JsonUtil.object_to_json(new_config)


def delete_flow(request):
    if request.method != 'DELETE':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)
    id = params.get('id')

    Flow.objects.filter(id=id).delete()

    return ResultMaker.success(id)


def get_module_tree(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    prompt_result_list = []
    prompt_count = 0

    keywords = request.GET.get('keyWords')
    prompt_scene_sql = 'select id,name from class where "type" = \'scene\''
    scene_list = DatabaseUtil.query(query_sql=prompt_scene_sql, return_dict=True)

    for scene in scene_list:
        scene_id = scene['id']
        # query prompt by scene_id
        prompt_list = __query_prompt(scene_id, keywords)
        scene = {
            "id": scene_id,
            "name": scene['name'],
            "type": "scene",
            "child_count": prompt_list.__len__(),
            "childs": prompt_list
        }
        prompt_count += prompt_list.__len__()
        prompt_result_list.append(scene)

    query_define_prompt_sql = 'select "id","name",\'prompt\' as "type",null as "prompt",null as "role_id",null as "role_name" from "module" where id = %s'
    query_define_prompt_param = ['00000000-0000-0000-aaaa-000000000001']
    if keywords:
        query_define_prompt_sql += ' and "name" like %s'
        query_define_prompt_param.append('%' + keywords + '%')
    define_prompt = DatabaseUtil.query(query_define_prompt_sql, query_define_prompt_param, True)
    prompt_count += define_prompt.__len__()

    define_prompt_scene = {
        "id": "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz",
        "name": 'Define Prompt',
        "type": "scene",
        "child_count": define_prompt.__len__(),
        "childs": define_prompt
    }
    prompt_result_list.append(define_prompt_scene)

    if keywords:
        tools = Module.objects.filter(Q(group='tool') & Q(name__contains=keywords))
        scripts = Module.objects.filter(Q(group='vectordb') & Q(name__contains=keywords))
    else:
        tools = Module.objects.filter(group='tool')
        scripts = Module.objects.filter(group='vectordb')

    result = [
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "name": "prompt",
            "child_count": prompt_count,
            "childs": prompt_result_list
        },
        {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "name": "tool",
            "child_count": tools.count(),
            "childs": list(tools.values())
        },
        {
            "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "name": "vectordb",
            "child_count": scripts.count(),
            "childs": list(scripts.values())
        }
    ]

    return ResultMaker.success(result)


# query prompt by scene_id
def __query_prompt(scene_id, keywords):
    query_param = [scene_id]
    query_prompt_sql = 'select pt."id",pt."name",\'prompt\' as "type",pt."prompt",pt."role_id",c."name" as "role_name" from "prompt" pt left join class c on pt."role_id" = c."id" where pt."scene_id" = %s'
    if keywords:
        query_prompt_sql += ' and pt."name" like %s'
        query_param.append('%' + keywords + '%')
    return DatabaseUtil.query(query_prompt_sql, query_param, True)


def __create_define_prompt_node(id):
    module = Module.objects.get(id=id)
    # get model
    model_dict, model_params_value = model_service.generate_template_model_param()
    template = PMPromptTemplate(template_content="")
    node = PMFlowTemplateNode(template=template, model=model_dict, model_params_value=model_params_value)
    node.module_id = module.id
    node.module_name = module.name
    return node


def __create_prompt_node(id):
    # get template
    prompt = Prompt.objects.get(id=id)
    role_name, role_template = prompt_service.generate_template_role_info(role_id=prompt.role_id)
    template = PMPromptTemplate(role=role_name, template_content=prompt.prompt, role_prompt=role_template)
    # get model
    model_dict, model_params_value = model_service.generate_template_model_param()
    # generate node
    node = PMFlowTemplateNode.from_template(template=template, model=model_dict,
                                            model_params_value=model_params_value)
    # package other info
    role_id_dict = {
        "name": "roleId",
        "type": "text",
        "defaultValue": prompt.role_id,
        "value": prompt.role_id
    }
    node.params['role'].insert(0, role_id_dict)
    node.module_id = prompt.id
    node.module_name = prompt.name
    return node


def __create_script_node(id):
    script_module = Module.objects.get(id=id)
    node = PMFlowScriptNode(module_id=script_module.id,
                            module_name=script_module.name,
                            module_type=script_module.type,
                            params=JsonUtil.json_to_dict(script_module.params),
                            inputs=JsonUtil.json_to_dict(script_module.inputs),
                            outputs=JsonUtil.json_to_dict(script_module.outputs))
    return node


def create_flow_node(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    id = params['id']
    type = params['type']
    try:
        if id == Constant.default_define_prompt_id:
            node = __create_define_prompt_node(id)
        elif type == 'prompt':
            node = __create_prompt_node(id)
        elif type == 'script' or type == 'vectordb':
            node = __create_script_node(id)
        else:
            raise exception.FLOW_MODULE_TYPE_NOT_SUPPORT
    except exception.FLOW_MODULE_TYPE_NOT_SUPPORT as e:
        logger.error(e)
        raise exception.FLOW_MODULE_TYPE_NOT_SUPPORT
    except Exception as e:
        logger.error(e)
        raise exception.FLOW_NODE_CREATE_ERROR

    node.id = None
    node.name = None
    return ResultMaker.success(JsonUtil.object_to_dict(node))


def get_pm_flow(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    try:
        flow = Flow.objects.get(id=request.GET.get('id'))
    except Exception as e:
        raise exception.FLOW_NOT_FOUND
    # json to dict
    if flow.config:
        flow.config = JsonUtil.json_to_dict(flow.config)
    if flow.params:
        flow.params = JsonUtil.json_to_dict(flow.params)
    if flow.model_ids:
        flow.model_ids = JsonUtil.json_to_dict(flow.model_ids)
    return ResultMaker.success(JsonUtil.object_to_dict(flow))


def save_pm_flow(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    # calculate prompt count and model_ids
    prompt_count, model_ids = __calculate_prompt_count_and_module_ids(params['nodes'])
    config = {
        "nodes": params['nodes'],
        "edges": params['edges']
    }

    # get input variables
    input_variables = PMFlow.get_flow_input_params(params['nodes'], params['edges'])

    # query flow and update flow
    Flow.objects.filter(id=params['id']).update(prompt_count=prompt_count, model_ids=JsonUtil.object_to_json(model_ids),
                                                params=JsonUtil.object_to_json(input_variables),
                                                config=JsonUtil.object_to_json(config), update_time=time.time())

    return ResultMaker.success(params['id'])


def __calculate_prompt_count_and_module_ids(nodes):
    prompt_count = 0
    module_ids = []
    for node in nodes:
        if node['module_type'] == 'prompt':
            prompt_count += 1
            if 'model' not in node['params']:
                continue
            model_params = node['params']['model']
            for model_param in model_params:
                if model_param['name'] == 'modelId':
                    module_ids.append(model_param['value'])
                    break
    return prompt_count, module_ids


def publish_pm_flow(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)
    publish_type = params['publish_type']
    if PublishType.ADD.value == publish_type:
        id = __add_app(params)
    elif PublishType.UPDATE.value == publish_type:
        id = __update_app(params)
    else:
        raise exception.FLOW_PUBLISH_TYPE_NOT_SUPPORT
    return ResultMaker.success(id)


def get_pm_flow_variables(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    try:
        flow = Flow.objects.get(id=request.GET.get('flow_id'))
    except Exception as e:
        raise exception.FLOW_NOT_FOUND

    params = []
    if flow.params:
        params = JsonUtil.json_to_dict(flow.params)
    return ResultMaker.success(params)


def flow_running_check(pm_flow: PMFlow):
    import multiprocessing
    lock = multiprocessing.Lock()
    lock.acquire()

    flow_result_path = pm_flow.generate_flow_result_path()
    content = FileUtil.read(file_path=flow_result_path)
    if content:
        flow_dict = PMCommonUtil.json_to_dict(content)
        if flow_dict['status'] == PMFlowStatus.RUNNING.name:
            raise exception.FLOW_IS_ON_RUNNING_NOW
        else:
            # delete flow info
            FileUtil.delete_file(flow_result_path)
            FileUtil.delete_file(file_path=pm_flow.generate_flow_output_path())

    lock.release()


def run_pm_flow(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)
    id = params['id']
    variables = params['variables']
    for variable in variables:
        if PMCommonUtil.is_value_none("value", variable):
            raise exception.FLOW_RUN_VARIABLES_CAN_NOT_NULL

    try:
        flow = Flow.objects.get(id=id)
    except Exception as e:
        raise exception.FLOW_NOT_FOUND

    if flow.config:
        flow.config = JsonUtil.json_to_dict(flow.config)

    nodes = flow.config['nodes']
    edges = flow.config['edges']
    pm_flow = PMFlow(id=flow.id, name=flow.name, nodes=nodes, edges=edges)

    # judge current flow is running or not
    flow_running_check(pm_flow=pm_flow)
    # pm_flow.show_info()

    pm_flow.run(variables=variables)
    result = {
        "result": id
    }
    return ResultMaker.success(result)


def get_pm_flow_run_status(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    id = request.GET.get('id')
    file_path = Path(__file__).resolve().parent.parent / ("flow/%s/flow_running.info" % id)
    running_info = FileUtil.read(file_path)
    if running_info:
        running_info = PMCommonUtil.json_to_dict(running_info)
    return ResultMaker.success(running_info)

def __add_app(params):
    flow_id = params['flow_id']
    flow = Flow.objects.get(id=flow_id)
    params['input_info'] = flow.params
    return app_service.add(params)


def __update_app(params):
    flow_id = params['flow_id']
    flow = Flow.objects.get(id=flow_id)
    params['input_info'] = flow.params
    return app_service.update(params)


def save_script_file(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    db_save_path, script_path, script_parent_path = __get_script_path(params['flow_id'], params['node_id'])
    if not os.path.exists(script_path):
        if not os.path.exists(script_parent_path):
            os.makedirs(script_parent_path)

    with open(script_path, "w") as f:
        f.write(params['script_content'])

    result = {
        "script_path": db_save_path
    }
    return ResultMaker.success(result)


def get_script_content(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    flow_id = request.GET.get('flow_id')
    node_id = request.GET.get('node_id')

    db_save_path, script_path, script_parent_path = __get_script_path(flow_id, node_id)
    if os.path.exists(script_path):
        with open(script_path, "r") as f:
            content = f.read()
    else:
        content = ""

    result = {
        "script_content": content
    }
    return ResultMaker.success(result)


def __get_script_path(flow_id, node_id):
    from pathlib import Path

    script_parent_relative_path = "flow/%s/%s" % (flow_id, node_id)
    script_relative_path = script_parent_relative_path + "/main.py"

    script_parent_absolute_path = Path(__file__).resolve().parent.parent / script_parent_relative_path
    script_absolute_path = Path(__file__).resolve().parent.parent / script_relative_path

    db_save_path = "%s/main.py" % node_id
    return db_save_path, script_absolute_path, script_parent_absolute_path
