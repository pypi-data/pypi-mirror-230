import unittest

import pytest

from test_project.src.network.APIRequest import APIRequest, StatusCodes
from test_project.src.utils import Config, Constants
from test_project.src.utils.APIConstants import OTTEndpoints
from test_project.src.utils.BaseHeader import OTTHeaders


class TestApi(unittest.TestCase):
    apiRequest = None
    headers = None
    payload = None

    @pytest.fixture(autouse=True, scope="class")
    def setup(self):
        self.apiRequest = APIRequest(base_url=Config.Environment['orprod']['ott_url'])
        self.headers = OTTHeaders()

    def test_01_ott_configuration(self):
        response = self.apiRequest.getRequest(OTTEndpoints.CONFIG,
                                              headers=self.headers.getHeaders())

        assert StatusCodes.OK.value == response.code, Constants.INVALID_RESPONSE_CODE
