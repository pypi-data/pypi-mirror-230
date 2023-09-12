import requests
import operator
import json
import logging

from promptmanager.runtime.common_util import PMCommonUtil
from promptmanager.runtime.exception import model_exception

logger = logging.getLogger('root')

proxy = {
    "http": "http://192.168.3.212:1088",
    "https": "http://192.168.3.212:1088"
}

class PMBaseAIModel:
    def __init__(self, config, params_define):
        self.config = config
        self.params_define = params_define
        content_path = PMLLM.get_model_result_path(config, params_define, '${result_context}')
        result_path = PMLLM.get_model_result_path(config, params_define, '${system_result}', replace_result=True)
        message_path = PMLLM.get_model_message_path(config, params_define, 'message')
        error_messge_path = PMLLM.get_model_error_message_path(config, params_define, '${errorMessage}')
        model_role = PMLLM.get_model_role(config, params_define)
        self._content_path = content_path
        self._result_path = result_path
        self._message_path = message_path
        self._error_messge_path = error_messge_path
        self._model_role = model_role

    def show_params_info(self):
        return PMCommonUtil.object_to_dict(self.params_define)

    @staticmethod
    def base_request(method, url, header, requestBody):
        method_lower_str = str(method).lower()
        if method_lower_str == 'get':
            response = requests.get(url=url)
        elif method_lower_str == 'post':
            response = requests.post(url=url, headers=header, json=requestBody, proxies=proxy)
        else:
            raise model_exception.UNSUPPORTED_REQUEST_METHOD()

        return response

    def request(self, requestBody, params=None):
        config = self.config
        params_define = self.params_define

        params_config = PMBaseAIModel.get_param_config(config, params_define, params, check_default_value=True)
        url = params_config['url']
        header = params_config['header']
        message = requestBody['messages']
        requestBody['messages'] = PMBaseAIModel.replace_message_role(self, message)

        response = PMBaseAIModel.base_request('POST', url, header, requestBody)
        response_text = response.text
        if response.status_code != 200 and PMCommonUtil.is_json(response_text):
            try:
                error_message = PMBaseAIModel.get_error_message(self, json.loads(response_text))
            except Exception as e:
                error_message = response_text
            raise model_exception.REQUEST_ERROR(10006, error_message)
        try:
            return json.loads(response_text)
        except Exception as e:
            return str(response_text)

    def get_error_message(self, response_text):
        for key in self._error_messge_path:
            response_text = response_text[key]
        return response_text

    @staticmethod
    def get_param_config(config, params_define, params=None, message=None, replace_result=False, check_default_value=False):
        # first filter by custom params
        if params:
            if isinstance(params, dict):
                for key in params:
                    param_name = '${' + key + '}'
                    if param_name == '${message}':
                        raise model_exception.MESSAGE_PARAM_UNSUPPORTED_CUSTOM
                    if param_name == '${result}':
                        raise model_exception.RESULT_PARAM_UNSUPPORTED_CUSTOM
                    if param_name == '${errorMessage}':
                        continue
                    param_value = params[key]
                    config = config.replace(param_name, str(param_value))
            elif isinstance(params, list):
                for param in params:
                    if PMCommonUtil.is_value_none('value', param):
                        logger.info('param value not exists')
                        continue
                    param_name = '${' + param['name'] + '}'
                    if param_name == '${message}':
                        raise model_exception.MESSAGE_PARAM_UNSUPPORTED_CUSTOM
                    if param_name == '${result}':
                        raise model_exception.RESULT_PARAM_UNSUPPORTED_CUSTOM
                    if param_name == '${errorMessage}':
                        continue
                    param_value = param['value']
                    config = config.replace(param_name, str(param_value))
            else:
                raise model_exception.UNSUPPORTED_PARAMS_TYPE()

        # second filter by params_define
        for param in params_define:
            param_name = '${' + param['name'] + '}'
            if not operator.contains(config, param_name):
                continue
            if param_name == '${errorMessage}':
                continue
            if operator.contains(str(param['type']).lower(), 'json'):
                default_value = param['defaultValue']
            else:
                default_value = str(param['defaultValue'])
            if str(param['type']).lower() == 'select':
                default_values = default_value.split(';')
                default_value = default_values[0]
            value = None
            param_value = default_value
            if 'value' in param:
                if param['value'] is not None:
                    value = str(param['value'])
            if param_name == '${message}':
                value = message
            if value:
                param_value = value
            if operator.contains(str(param['type']).lower(), 'json'):
                param_value = PMCommonUtil.object_to_json(param_value)
            if replace_result:
                if param_name == '${result}':
                    param_value = '\"${system_result}\"'
            if check_default_value and param_name != '${errorMessage}' and not default_value:
                raise model_exception.DEFAULT_VALUE_IS_REQUIRED()
            config = config.replace(param_name, param_value)

        config = config.replace('True', 'true')
        config = config.replace('False', 'false')
        config = config.replace('None', 'null')
        return json.loads(config)

    def replace_message_role(self, message):
        model_role = self._model_role
        for msg in message:
            role = msg['role']
            if role in model_role:
                msg['role'] = model_role[role]
        return message

    def request_result(self, requestBody, params):
        response = self.request(requestBody, params)
        result = PMBaseAIModel.get_response_result(response, self.__content_path)
        if not result:
            result = PMBaseAIModel.get_response_result(response, self.__result_path)
        return result

    @staticmethod
    def get_response_path(responseBody, value):
        result_path = ''
        for path in PMCommonUtil.find_path(responseBody, value, []):
            result_path = path
        return result_path

    @staticmethod
    def  get_response_path_by_key(responseBody, key):
        result_path = ''
        for path in PMCommonUtil.find_path_by_key(responseBody, key, []):
            result_path = path
        return result_path

    @staticmethod
    def get_response_result(response, result_path):
        for key in result_path:
            response = response[key]
        return response


class PMLLM(PMBaseAIModel):
    @staticmethod
    def load_from_config(config, params_define):
        return PMLLM(config, params_define)

    @staticmethod
    def load_from_path(path):
        with open(path, 'r') as file:
            content = json.load(file)
        config = content['config']
        params = content['params']
        return PMLLM.load_from_config(config, params)

    @staticmethod
    def get_model_result_path(config, params_define, target_result, replace_result=False):
        config_content = PMLLM.get_param_config(config, params_define, replace_result=replace_result)
        responseBody = PMCommonUtil.object_to_dict(config_content['responseBody'])
        result_path = PMBaseAIModel.get_response_path(responseBody, target_result)
        return result_path

    @staticmethod
    def get_model_error_message_path(config, params_define, target_result):
        config_content = PMLLM.get_param_config(config, params_define)
        responseErrorBody = PMCommonUtil.object_to_dict(config_content['responseErrorBody'])
        error_message_path = PMBaseAIModel.get_response_path(responseErrorBody, target_result)
        return error_message_path

    @staticmethod
    def get_model_role(config, params_define):
        config_content = PMLLM.get_param_config(config, params_define)
        modelRole = PMCommonUtil.object_to_dict(config_content['modelRole'])
        return modelRole

    def request_by_message(self, message, params=None):
        config = self.config
        params_define = self.params_define

        params_config = PMBaseAIModel.get_param_config(config, params_define, params, message, check_default_value=True)
        url = params_config['url']
        header = params_config['header']
        requestBody = params_config['requestBody']

        response = PMBaseAIModel.base_request('POST', url, header, requestBody)
        response_text = response.text
        if response.status_code != 200 and PMCommonUtil.is_json(response_text):
            try:
                error_message = PMBaseAIModel.get_error_message(self, json.loads(response_text))
            except Exception as e:
                error_message = response_text
            raise model_exception.REQUEST_ERROR(10006, error_message)
        try:
            return json.loads(response_text)
        except Exception as e:
            return str(response_text)

    def request_result_by_message(self, message, params=None):
        params_config = PMLLM.get_param_config(self.config, self.params_define, params, message, check_default_value=True)
        requestBody = params_config['requestBody']
        response = PMBaseAIModel.request(self, requestBody, params)
        result = PMBaseAIModel.get_response_result(response, self._content_path)
        if not result:
            result = PMBaseAIModel.get_response_result(response, self._result_path)
        return result

    def request_message(self, message, params=None):
        params_config = PMLLM.get_param_config(self.config, self.params_define, params, message, check_default_value=True)
        requestBody = params_config['requestBody']
        response = PMBaseAIModel.request(self, requestBody, params)
        result = PMBaseAIModel.get_response_result(response, self._message_path)
        if not result:
            result = PMBaseAIModel.get_response_result(response, self._result_path)
        return result

    @classmethod
    def get_model_message_path(cls, config, params_define, target_result):
        config_content = PMLLM.get_param_config(config, params_define, replace_result=False)
        responseBody = PMCommonUtil.object_to_dict(config_content['responseBody'])
        result_path = PMBaseAIModel.get_response_path_by_key(responseBody, target_result)
        return result_path


class PMOpenAIPMLLM(PMLLM):
    @staticmethod
    def load_from_openai_key(api_key):
        file_path = '../model/default/openapi_model.conf'
        with open(file_path, 'r') as file:
            content = json.load(file)
        config = content['config']
        config = config.replace('${OPENAI_API_KEY}', api_key)
        params = content['params']
        return PMLLM(config, params)


class PMFakeLLM(PMLLM):
    def __init__(self, response):
        self.response = response

    def request(self, requestBody, params=None):
        config = self.config
        params_define = self.params_define

        params_config = PMBaseAIModel.get_param_config(config, params_define, params, check_default_value=True)
        url = params_config['url']
        header = params_config['header']

        return PMFakeLLM.get_result(self.response)

    def request_by_message(self, message, params=None):
        config = self.config
        params_define = self.params_define

        params_config = PMBaseAIModel.get_param_config(config, params_define, params, message, check_default_value=True)
        url = params_config['url']
        header = params_config['header']
        requestBody = params_config['requestBody']

        return PMFakeLLM.get_result(self.response)

    def request_result_by_message(self, message, params=None):
        params_config = PMLLM.get_param_config(self.config, self.params_define, params, message,
                                               check_default_value=True)
        requestBody = params_config['requestBody']

        return PMFakeLLM.get_result(self.response)

    @staticmethod
    def get_result(response):
        result = ''
        for line in response:
            result = result + line + '\n'
        return result


class PMCustomLLM(PMLLM):
    pass