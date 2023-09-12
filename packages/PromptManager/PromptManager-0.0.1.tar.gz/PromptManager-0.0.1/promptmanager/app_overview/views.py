from django.http import FileResponse

from promptmanager.app_common.database_util import DatabaseUtil
from promptmanager.app_common.result_maker import ResultMaker
from promptmanager.PromptManager.settings import base

from promptmanager.exception import exception


def component(request):
    if request.method != 'GET':
        raise exception.REQUEST_TYPE_NOT_SUPPORT()

    prompt_count = DatabaseUtil.query(query_sql='select count(*) from prompt')
    model_count = DatabaseUtil.query(query_sql='select count(*) from model')
    flow_count = DatabaseUtil.query(query_sql='select count(*) from flow')
    app_count = DatabaseUtil.query(query_sql='select count(*) from app')

    result = {
        'prompt': prompt_count[0][0],
        'model': model_count[0][0],
        'flow': flow_count[0][0],
        'app': app_count[0][0]
    }

    return ResultMaker.success(result)

def qucikguide(request):
    path = base.QUICK_GUIDE_FILE_PATH
    name = path[path.rindex('/') + 1: len(path)]
    return FileResponse(open(path, 'rb'), filename=name)