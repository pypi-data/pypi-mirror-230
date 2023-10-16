import json

from model_service.utils.constants import Constants
from model_service.utils.exceptions import NotFoundError
from model_service.utils.ms_requests import MsSession
from model_service.utils.torch_respon_data import TorchResponseData


class ModelInferenceClient:
    def __init__(self, url):
        self.session = MsSession.new_session()
        self._headers = {
            'User-Agent': Constants.HEADER_USER_AGENT,
            'Content-Type': Constants.HEADER_CONTENT_TYPE
        }
        self._timeout = 60
        self.inference_url = url

    def inference(self, model_name, data):
        url = self.inference_url + "/predictions/" + model_name
        response = self.session.put(url, data=json.dumps(data), headers=self._headers,
                                    timeout=self._timeout)
        if response.status_code == 200:
            return TorchResponseData(json.loads(response.content)).data
        else:
            raise NotFoundError("failed to inference from model_service: {}".format(response.content))
