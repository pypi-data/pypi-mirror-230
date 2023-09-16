from test_project.src.utils.APIConstants import EndPoints
from test_project.src.network.APIRequest import APIRequest
import json

from test_project.src.utils.BaseHeader import BaseHeaders
from test_project.src.utils.Payloads import Payloads


class EnrollDeviceRequest:

    def __init__(self, **kwargs):
        self.request = APIRequest()
        self.body = Payloads().enroll_payload(**kwargs)
        self.headers = BaseHeaders().get_enroll_device_headers(**kwargs)

    def prepare_request(self):
        response = self.request.postRequest(url_endpoint=EndPoints.ENROLL,
                                            headers=self.headers(),
                                            payload=json.dumps(self.body))
        return response

