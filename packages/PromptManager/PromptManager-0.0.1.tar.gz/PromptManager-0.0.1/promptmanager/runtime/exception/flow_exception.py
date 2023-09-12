class ILLEGAL_EDGE_INFO(Exception):
    code = 10001
    message = u"edge info is illegal!!!"


class FLOW_INPUT_NOT_EXIST(Exception):
    code = 10002
    message = u"flow input is not exists!!!"


class FLOW_TARGET_NODE_INPUT_NOT_MATCH(Exception):
    code = 10003
    message = u"flow target node input not match!!!"


class FLOW_RUN_VARIABLES_ILLEGAL(Exception):
    code = 10004
    message = u"run flow variables illegal"


class Flow_NODE_NOT_EXIST(Exception):
    code = 10005
    message = u"flow node not exists"


class FLOW_RUN_EXCEPTION(Exception):
    code = 10006
    message = u"flow run exception"
