import json
import time
import uuid

from django.forms import model_to_dict
from django.core.paginator import Paginator

from promptmanager.app_common.constant import Constant
from promptmanager.app_common.enum_source_type import SourceType
from promptmanager.exception import exception

from promptmanager.app_app.models import App
from promptmanager.app_flow.models import Flow

from promptmanager.PromptManager.settings import base
from promptmanager.app_common.result_maker import ResultMaker
from promptmanager.app_common.json_util import JsonUtil
from promptmanager.app_common.http_request_util import HttpRequestUtil
from promptmanager.app_common.database_util import DatabaseUtil

def get_app_list(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    page_num = request.GET.get('pageIndex', 1)
    page_size = request.GET.get('pageNum', 15)
    order_key = request.GET.get('orderKey', 'update_time')
    order_by = request.GET.get('orderBy', 'desc')
    keywords = request.GET.get('keyWords', None)

    #"输入变量数"默认升序
    input_variables_order_by = False

    if order_key == 'input_variables':
        if order_by == 'desc':
            input_variables_order_by = True
        if keywords:
            query_result = App.objects.filter(name__contains=keywords)
        else:
            query_result = App.objects.all()
    else:
        if order_by == 'desc':
            order_key = '-' + order_key
        if keywords:
            query_result = App.objects.filter(name__contains=keywords).order_by(order_key)
        else:
            query_result = App.objects.all().order_by(order_key)

    app_url_properties = base.APP_URL
    result = []
    for app in list(query_result):
        app_dict = model_to_dict(app)
        #设置app的url
        app_dict['url'] = app_url_properties.replace('<appId>', app.id)
        #设置flow名称
        try:
            flow = Flow.objects.get(id=app.flow_id)
            flow_name = flow.name
        except Exception as e:
            flow_name = None
        app_dict['flow_name'] = flow_name
        #设置输入变量
        if JsonUtil.is_json(app.input_info):
            app_dict['input_variables'] = len(json.loads(app.input_info))
        else:
            app_dict['input_variables'] = 0
        try:
            app_dict['input_info'] = json.loads(app_dict['input_info'])
        except Exception as e:
            app_dict['input_info'] = app_dict['input_info']
        result.append(app_dict)

    if order_key == 'input_variables':
        result.sort(key = lambda x:x['input_variables'], reverse=input_variables_order_by)

    p = Paginator(result, page_size)
    page_data = p.page(page_num)

    page_result = {
        'count': len(result),
        'rows': list(page_data)
    }

    return ResultMaker.success(page_result)

def delete_app(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    app_id = params.get('id')
    try:
        app = App.objects.get(id=app_id)
    except Exception as e:
        raise exception.APP_NOT_EXISTS
    app.delete()

    return ResultMaker.success(app_id)

def check_name(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    app_name = request.GET.get('name', None)

    exist_obj = DatabaseUtil.query(query_sql='select count(*) from "app" where name = %s', params=[app_name])

    is_exist = False
    if exist_obj[0][0] > 0:
        is_exist = True

    result = {"exists": is_exist}
    return ResultMaker.success(result)


def update_app(request):
    if request.method != 'POST':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    params = HttpRequestUtil.get_http_request_body(request)

    app_id = params.get('id')
    app_name = params.get('name')
    try:
        app = App.objects.get(id=app_id)
    except Exception as e:
        raise exception.APP_NOT_EXISTS
    App.objects.filter(id=app_id).update(name=app_name)

    return ResultMaker.success(app_id)


def add(params):
    id = uuid.uuid4()
    app_name = params['app_name']
    description = app_name
    flow_id = params['flow_id']
    input_info = params['input_info']

    app = App(id=id, name=app_name, description=description, flow_id=flow_id, input_info=input_info,
              source=SourceType.USER.value, create_time=time.time(), update_time=time.time(),
              user_id=Constant.default_user_id)

    app.save()
    return id


def update(params):
    id = params['app_id']
    flow_id = params['flow_id']
    input_info = params['input_info']

    App.objects.filter(id=id).update(flow_id=flow_id,
                                     input_info=input_info,
                                     update_time=time.time())

    return id
