import requests

from promptmanager.runtime.flow import PMFlow

class PMApp:
    def __init__(self, pm_flow:PMFlow=None, base_url=None):
        self.pm_flow = pm_flow
        self.base_url = base_url

    def publish_from_flow(self, pmflow:PMFlow, base_url):
        #http://127.0.0.1:8888/api/app/518cd781-6ca4-401b-7202-4bb2c90ced4c/run
        #发布成app
        return 'ok'

    def run(self, variables):
        pm_flow = self.pm_flow
        #用已有的flow信息运行
        return None

    def run(url, variables):
        data = {'variables': variables}
        #http://127.0.0.1:8888/api/app/518cd781-6ca4-401b-7202-4bb2c90ced4c/run
        req = requests.post(url=url, data=data)
        return req.text

    def run(app_id):
        return None