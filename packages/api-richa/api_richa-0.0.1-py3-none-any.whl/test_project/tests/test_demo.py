import json

import pytest
import unittest

from test_project.src.Request.EnrollDeviceRequest import EnrollDeviceRequest
from test_project.src.network.APIRequest import StatusCodes
from test_project.src.network.APIRequest import APIRequest
from test_project.src.utils import Config
from test_project.src.utils.APIConstants import EndPoints
from test_project.src.utils.Payloads import Payloads
from test_project.src.utils.BaseHeader import BaseHeaders


class TestApi(unittest.TestCase):
    apiRequest = None
    headers = None
    payload = None
    post_id = None

    @pytest.fixture(autouse=True, scope="class")
    def setup(self):
        self.apiRequest = APIRequest(Config.Environment['orprod']['jsonplaceholder_url'])
        self.headers = BaseHeaders()
        self.payload = Payloads()

    # Post
    def test_001_enroll_device_post_api_call(self):
        enterprise_id = Config.APPConstants.ENTERPRISE_ID
        user_id = Config.APPConstants.USER_ID
        response = EnrollDeviceRequest(enterpriseId=enterprise_id, userId=user_id).prepare_request()
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    def test_002_emp_post_api_call(self):
        payload = self.payload.employee_payload(name="Aaaa", age="11", salary="10000")
        headers = self.get_emp_headers()
        response = self.apiRequest.postRequest(url_endpoint=EndPoints.EMPLOYEE_CREATE,
                                               headers=headers,
                                               payload=payload)
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    def test_003_create_post_api_call(self):
        payload = self.payload.create_post_payload(title="Aaaa", body="test_body")
        headers = self.headers.get_base_header()
        response = self.apiRequest.postRequest(url_endpoint=EndPoints.GET_POSTS,
                                               headers=headers,
                                               payload=payload)
        self.post_id = response.content.get('id')
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    # Get call
    def test_004_posts_get_api_call(self):
        response = self.apiRequest.getRequest(url_endpoint=EndPoints.GET_POSTS)
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    def test_005_comments_by_post_id_get_api_params_call(self):
        headers = self.headers.get_base_header()
        params = self.payload.comments_by_post_id_payload(postId=self.post_id)
        response = self.apiRequest.getRequest(url_endpoint=EndPoints.GET_COMMENTS_BY_POST_ID,
                                              headers=headers, params=params)
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    # Patch
    def test_006_post_patch_call(self):
        headers = self.headers.get_base_header()
        params = {'title': "test111111"}
        endPoint = EndPoints.GET_POSTS + "/1"
        response = self.apiRequest.patchRequest(url_endpoint=endPoint,
                                                headers=headers, payload=params)
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."

    # Put
    def test_007_post_put_call(self):
        headers = self.headers.get_base_header()
        params = self.payload.create_post_payload(title="Bbbbbbbb")
        endPoint = EndPoints.GET_POSTS + "/1"
        response = self.apiRequest.putRequest(url_endpoint=endPoint,
                                              headers=headers, payload=params)
        assert StatusCodes.OK.value == response.code or \
               StatusCodes.CREATED.value == response.code, "Unexpected status code."
