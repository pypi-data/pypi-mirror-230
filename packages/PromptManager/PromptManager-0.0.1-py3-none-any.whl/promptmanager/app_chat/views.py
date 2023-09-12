import json
import os.path
from datetime import datetime
from typing import Generator

import requests
from django.forms import model_to_dict
# Create your views here.
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

from promptmanager import exception
from promptmanager.PromptManager.settings import base
from promptmanager.app_common.http_request_util import HttpRequestUtil
from promptmanager.app_common.json_util import JsonUtil
from promptmanager.app_common.result_maker import ResultMaker
from promptmanager.app_model.models import Model
from promptmanager.app_model.views import get_contains_param_config
from promptmanager.runtime.exception import model_exception
from promptmanager.runtime.model import PMLLM, PMBaseAIModel
from promptmanager.runtime.template import PMPromptTemplate


def getParams(params):
    param_list = []
    for i in range(len(params)):
        paramDict = params[i]
        if "result" == paramDict['name'] or "message" == paramDict['name'] or "errorMessage" == paramDict['name']:
            continue
        else:
            param_list.append(paramDict)
    return param_list


def model_configuration(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    query_result = Model.objects.all().order_by('-update_time')

    result = []
    for model in list(query_result):
        model_dict = model_to_dict(model)
        param_config = get_contains_param_config(model.config, model.params)
        model_dict['params'] = getParams(JsonUtil.json_to_dict(model.params))
        model_dict['params_define'] = JsonUtil.json_to_dict(model.params)
        if JsonUtil.is_json(param_config):
            model_dict['url'] = JsonUtil.json_to_dict(param_config).get('url')
        else:
            model_dict['url'] = None
        
        result.append(model_dict)

    conf_list = {
        'count': len(result),
        'rows': result
    }

    return ResultMaker.success(conf_list)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = base.ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request):
    if request.method != "POST":
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    file = request.FILES.get('file', None)
    if file is None:
        raise exception.UPLOAD_FILE_CANNOT_BE_EMPTY()
    else:
        fileName = file.name
        if not allowed_file(fileName):
            raise exception.UPLOAD_FILE_TYPE_NOT_BE_ALLOWED()
        dir_root_path = base.PROMPT_FILE_UPLOAD_ROOT_PATH
        loca = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_root_Path = os.path.join(dir_root_path, str(loca))
        if not os.path.exists(file_root_Path):
            os.makedirs(file_root_Path)
        filePath = os.path.join(file_root_Path, fileName)
        with open(filePath, 'wb+') as f:
            #分块写文件
            for chunk in file.chunks():
                f.write(chunk)
        return ResultMaker.success(filePath)

def read_file(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    filePath = request.GET.get("filePath")
    if filePath and os.path.exists(filePath):
        read_char_length = base.CHAT_READ_FILE_MAX_LENGTH
        with open(filePath, "r") as f:
            content = f.read(read_char_length)
        return ResultMaker.success(json.load(content))
    else:
        return ResultMaker.success("")


def get_messages_by_prompts(prompts):
    messages = []
    for prompt in prompts:
        role = prompt.get('role', "")
        role_prompt = prompt.get('role_prompt', "")
        template_content = prompt.get('template_content', None)
        variables = prompt.get('prompt_variables', None)
        if not template_content:
            raise exception.PROMPT_CONTENT_CANNOT_BE_EMPTY

        prompt = PMPromptTemplate(role, template_content, role_prompt)
        message = prompt.message(variables, True)
        messages.extend(message)
    return messages


def sync_chat_completions(request):
    resut_dict = {}
    resut_dict['role'] = 'assistant'
    if request.method != "POST":
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    params = HttpRequestUtil.get_http_request_body(request)
    prompts = params.get("prompts", [])
    model_params_define = params.get("params_define", None)
    model_params = params.get("model_params", None)
    config = params.get("config", None)
    if not prompts or len(prompts) == 0:
        raise exception.CHAT_COMPLETIONS_MESSAGE_CANNOT_BE_EMPTY()
    if not model_params_define:
        raise exception.CHAT_COMPLETIONS_PARAMS_CANNOT_BE_EMPTY()
    if not config:
        raise exception.CHAT_COMPLETIONS_CONFIG_CANNOT_BE_EMPTY()
    if not model_params:
        raise exception.CHAT_COMPLETIONS_MODEL_PARAMS_CANNOT_BE_EMPTY()
    try:
        messages = get_messages_by_prompts(prompts)
        pmllm = PMLLM.load_from_config(config, model_params_define)
        result = pmllm.request_result_by_message(messages, model_params)
        resut_dict['content'] = result
        resut_dict['status'] = 'success'
    except Exception as e:
        if isinstance(e, (model_exception.REQUEST_ERROR, exception.FILE_NOT_EXIST)):
            resut_dict['content'] = e.message
        else:
            resut_dict['content'] = str(e)
        resut_dict['status'] = 'fail'
    return ResultMaker.success(resut_dict)

@csrf_exempt
def async_chat_completions(request):
    if request.method != "POST":
        raise exception.REQUEST_TYPE_NOT_SUPPORT()
    headers = {'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'}
    params = HttpRequestUtil.get_http_request_body(request)
    prompts = params.get("prompts", [])
    model_params_define = params.get("params_define", None)
    model_params = params.get("model_params", None)
    config = params.get("config", None)
    if not prompts or len(prompts) == 0:
        raise exception.CHAT_COMPLETIONS_MESSAGE_CANNOT_BE_EMPTY()
    if not model_params_define:
        raise exception.CHAT_COMPLETIONS_PARAMS_CANNOT_BE_EMPTY()
    if not config:
        raise exception.CHAT_COMPLETIONS_CONFIG_CANNOT_BE_EMPTY()
    if not model_params:
        raise exception.CHAT_COMPLETIONS_MODEL_PARAMS_CANNOT_BE_EMPTY()
    try:
        messages = get_messages_by_prompts(prompts)
        pmllm = PMLLM.load_from_config(config, model_params_define)
        params_config = PMLLM.get_param_config(config, model_params_define, model_params, messages,
                                               check_default_value=True)
        requestBody = params_config['requestBody']
        url = params_config['url']
        header = params_config['header']
        message = requestBody['messages']
        requestBody['messages'] = pmllm.replace_message_role(message)

        #调用模型 封装在runtime里
        chat_proxy_host = base.CHATGPT_PROXY_HOST
        chat_proxy_port = base.CHATGPT_PROXY_PORT
        # API_KEY = base.OPENAI_API_KEY
        # 设置代理服务器IP
        proxies = {'https': chat_proxy_host + ":" + str(chat_proxy_port),
                   'http': chat_proxy_host + ":" + str(chat_proxy_port)}

        api_response = requests.Session().post(url, headers=header, json=requestBody, proxies=proxies, stream=True, )

    except Exception as e:
        event_name = 'error'
        str_out = f'event: {event_name}\ndata: {str(e)}\n\n'
        return StreamingHttpResponse(str_out, content_type="text/event-stream", headers=headers)

    def performRequestWithStreaming(api_response):
        if api_response.status_code == 200:
            streams = get_stream(api_response)
            for stream in streams:
                stream = stream.decode("utf-8")[6:]
                if stream == "[DONE]":
                    event_name = 'close'
                else:
                    event_name = 'message'
                    rsp: dict = json.loads(stream)
                    choices = rsp.get("choices")
                    if not choices:
                        continue
                    delta = choices[0].get("delta")
                    if not delta:
                        continue
                    if "role" in delta:
                        delta['role'] = 'assistant'
                str_out = f'event: {event_name}\ndata: {JsonUtil.object_to_json(delta)}\n\n'
                yield str_out
        else:
            delta = api_response.text
            event_name = 'error'
            str_out = f'event: {event_name}\ndata: {JsonUtil.object_to_json(delta)}\n\n'
            yield str_out

    def get_stream(api_response) -> Generator:
        for line in api_response.iter_lines():
            print(line)
            if not line:
                continue
            yield line


    return StreamingHttpResponse(performRequestWithStreaming(api_response), content_type="text/event-stream", headers=headers)

@csrf_exempt
def async_chat_completions_get(request):
    #调用模型
    chat_proxy_host = base.CHATGPT_PROXY_HOST
    chat_proxy_port = base.CHATGPT_PROXY_PORT
    API_KEY = base.OPENAI_API_KEY
    # 设置代理服务器IP
    proxies = {'https': chat_proxy_host + ":" + str(chat_proxy_port),
               'http': chat_proxy_host + ":" + str(chat_proxy_port)}
    reqUrl = 'https://api.openai.com/v1/chat/completions'
    reqHeaders = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer '+API_KEY
    }
    prompts = [{
        "role": "teacher",
        "content": "请写一篇500字科幻小说外星人的小狗"
    }]
    reqBody = {
        "model": "gpt-3.5-turbo",
        "messages": prompts,
        "max_tokens": 2048,
        "temperature": 0.6,
        "top_p": 1.0,
        "stream": True,
    }
    api_response = requests.Session().post(reqUrl, headers=reqHeaders, json=reqBody, proxies=proxies, stream=True, )
    # except Exception as e:
    #     if isinstance(e, (model_exception.REQUEST_ERROR, exception.FILE_NOT_EXIST)):
    #         resut_dict['content'] = e.message
    #     else:
    #         resut_dict['content'] = str(e)
    #     resut_dict['status'] = 'fail'

    def performRequestWithStreaming(api_response):
        if api_response.status_code == 200:
            streams = get_stream(api_response)
            for stream in streams:
                stream = stream.decode("utf-8")[6:]
                if stream == "[DONE]":
                    event_name = 'close'
                else:
                    event_name = 'message'
                    rsp: dict = json.loads(stream)
                    choices = rsp.get("choices")
                    if not choices:
                        continue
                    delta = choices[0].get("delta")
                    if not delta:
                        continue
                    if "role" in delta:
                        delta['role'] = 'assistant'
                str_out = f'event: {event_name}\ndata: {JsonUtil.object_to_json(delta)}\n\n'
                yield str_out
        else:
            delta = api_response.text
            event_name = 'error'
            str_out = f'event: {event_name}\ndata: {JsonUtil.object_to_json(delta)}\n\n'
            yield str_out

    def get_stream(api_response) -> Generator:
        for line in api_response.iter_lines():
            print(line)
            if not line:
                continue
            yield line

    headers = {'Cache-Control': 'no-cache'}
    return StreamingHttpResponse(performRequestWithStreaming(api_response), content_type="text/event-stream", headers=headers)

