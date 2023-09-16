import unittest

import pytest

from test_project.src.network.APIRequest import APIRequest, StatusCodes
from test_project.src.utils import Config, Constants
from test_project.src.utils.APIConstants import VMAEndpoints
from test_project.src.utils.BaseHeader import VMAHeaders
from test_project.src.utils.Payloads import VMAPayloads


class TestApi(unittest.TestCase):
    apiRequest = None
    headers = None
    payload = None

    @pytest.fixture(autouse=True, scope="class")
    def setup(self):
        self.apiRequest = APIRequest(base_url=Config.Environment['orprod']['vma_url'])
        self.headers = VMAHeaders()
        self.payload = VMAPayloads()

    def test_01_vma_provisioning(self):
        payload = self.payload.get_provisioning_payload(mdn=Constants.VMAConstants.MDN, deviceId=Constants.VMAConstants.DEVICE_ID,
                                                          loginToken=Constants.VMAConstants.LOGIN_TOKEN)
        response = self.apiRequest.postRequest(url_endpoint=VMAEndpoints.PROVISIONING, payload=payload,
                                               headers=self.headers.getHeaders())
        assert StatusCodes.OK.value == response.code, Constants.INVALID_RESPONSE_CODE



