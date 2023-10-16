import json
import time
import paramiko
from scp import SCPClient

from model_service.utils.exceptions import NotFoundError
from model_service.utils.constants import Constants
from model_service.utils.ms_requests import MsSession
from model_service.utils.respon_data import ResponseData


class ModelLaunchClient:
    def __init__(self, url):
        self.manager_url = url
        self.session = MsSession.new_session()
        store_params = self.get_store_params(url + "/api/in/store")
        self.host = store_params.get("host")
        self.port = store_params.get("port")
        self.username = store_params.get("username")
        self.password = store_params.get("password")
        self._headers = {
            'User-Agent': Constants.HEADER_USER_AGENT,
            'Content-Type': Constants.HEADER_CONTENT_TYPE
        }
        self._timeout = 360
        self.inference_url = ""

    def config(self, model_id, torchserve_id):
        if (model_id is not None) and (torchserve_id is not None):
            self.model_id = model_id
            self.torchserve_id = torchserve_id

    def get_store_params(self, url):
        response = self.session.get(url)
        if response.status_code == 200:
            return ResponseData(json.loads(response.content)).result
        else:
            raise NotFoundError("[ERROR] can't get results: {}".format(response.content))

    def upload(self, env, source_path, model_name):
        ts = int(time.time())
        target_path = Constants.FTP_INTRANET_PATH.format(env, model_name, ts)

        if source_path.endswith("*"):
            source_path = source_path.strip('*')
        elif not source_path.endswith("/"):
            source_path += "/"
        print("[INFO] local path: ", source_path)
        print("[INFO] remote path: ", target_path)
        print("[INFO] start uploading now, please wait a minute....")

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh_client.connect(self.host, self.port, self.username, str(self.password))
        ssh_client.exec_command('mkdir -p ' + target_path)
        scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=30.0)

        try:
            scpclient.put(source_path, target_path, recursive=True)
        except FileNotFoundError as e:
            raise NotFoundError(e, "[ERROR] failed to upload model files: source_path is {}".format(source_path))
        else:
            print("[INFO] upload success!")
        scpclient.close()
        ssh_client.close()
        return model_name + "_" + str(ts)

    def package(self, model_id=None, torchserve_id=None):
        self.config(model_id, torchserve_id)

        url = self.manager_url + "/api/in/package"
        data = {
            "model_id": self.model_id,
            "torchserve_id": self.torchserve_id
        }
        response = self.session.post(url, data=json.dumps(data), headers=self._headers, timeout=self._timeout)
        if response.status_code == 200:
            print("[INFO] package success!")
            return ResponseData(json.loads(response.content))
        else:
            raise NotFoundError("[ERROR] failed to package model: {}".format(response.content))

    def distribute(self, model_id=None, torchserve_id=None):
        self.config(model_id, torchserve_id)
        url = self.manager_url + "/api/in/distribute"
        data = {
            "model_id": self.model_id,
            "torchserve_id": self.torchserve_id
        }
        response = self.session.post(url, data=json.dumps(data), headers=self._headers, timeout=self._timeout)
        if response.status_code == 200:
            print("[INFO] distribute success!")
            return ResponseData(json.loads(response.content))
        else:
            raise NotFoundError("[ERROR] failed to distribute model: {}".format(response.content))

    def list_models(self, model_name=None):
        url = self.manager_url + "/api/in/models"
        if model_name is not None:
            url += "?model_name={}".format(model_name)
        response = self.session.get(url)
        if response.status_code == 200:
            return ResponseData(json.loads(response.content))
        else:
            raise NotFoundError("[ERROR] failed to get models: {}".format(response.content))

    def launch(self, model_id=None, torchserve_id=None):
        self.config(model_id, torchserve_id)
        print("[INFO] 1/3 start packaging now, please wait a minute....")
        self.package()
        print("[INFO] 2/3 start distributing now, please wait a minute....")
        self.distribute()
        print("[INFO] 3/3 start launching now, please wait a minute....")
        return self.final_launch()

    def final_launch(self, model_id=None, torchserve_id=None):
        self.config(model_id, torchserve_id)
        url = self.manager_url + "/api/in/launch"
        data = {
            "model_id": self.model_id,
            "torchserve_id": self.torchserve_id
        }
        response = self.session.post(url, data=json.dumps(data), headers=self._headers, timeout=self._timeout)
        if response.status_code == 200:
            self.inference_url = ""
            res = ResponseData(json.loads(response.content))
            print("[INFO] launch success! ", res.message)
            return res
        else:
            raise NotFoundError("[ERROR] failed to launch model_service: {}".format(response.content))

    # def inference(self, data):
    #     self.inference_url += ""
    #     response = self.session.put(self.inference_url, data=json.dumps(data), headers=self._headers,
    #                                 timeout=self._timeout)
    #     if response.status_code == 200:
    #         return ResponseData(json.loads(response.content))
    #     else:
    #         raise NotFoundError("failed to launch model_service: {}".format(response.content))

    def generate_handler_example(self, param):
        file_handler = open(param + "handler.py", 'w')
        file_input = open(param + "input.json", 'w')

        tmp = open("./example/handler.py", 'r').read()
        print(tmp)

        json = '''[
      {
        "field_a": 833.0,
        "field_b": 27.0
      },
      {
        "field_a": -28.0,
        "field_b": -1.0
      }
    ]
        '''

        file_handler.write(tmp)  # 写入内容信息
        file_input.write(json)
        file_handler.close()
        file_input.close()
        print('ok')
