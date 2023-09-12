class UNSUPPORTED_REQUEST_METHOD(Exception):
    code = 10001
    message = u"unsupported request method"

class UNSUPPORTED_PARAMS_TYPE(Exception):
    code = 10002
    message = u"unsupportes params type"

class DEFAULT_VALUE_IS_REQUIRED(Exception):
    code = 10003
    message = u"default value is required"

class MESSAGE_PARAM_UNSUPPORTED_CUSTOM(Exception):
    code = 10004
    message = u"message param unsupported custom"

class RESULT_PARAM_UNSUPPORTED_CUSTOM(Exception):
    code = 10005
    message = u"result param unsupported custom"

class REQUEST_ERROR(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
