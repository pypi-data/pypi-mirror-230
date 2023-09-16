from test_project.src.utils import Constants


class BaseHeaders:

    def get_base_header(self):
        return {
            'Content-Type': 'application/json'
        }

    def get_enroll_device_headers(self, **kwargs):
        return {
            'Content-Type': 'application/json',
            'bjToken': 'ucaas_' + str(kwargs.get('enterpriseId')) + '_' + str(kwargs.get('userId')),
            # 'bjToken': 'ucaas_1028010_5947632',
            'User-Agent': 'UCaaS/2.45.0/8.9/55/mac/(MacBook; mac 13.4.0)'
        }

    def get_emp_headers(self):
        return {
            'Content-Type': 'application/json',
            'Content-Length': '1024',
            'Accept': '*/*',
            'Host': 'dummy.restapiexample.com',
            'User-Agent': 'UCaaS/2.45.0/8.9/55/mac/(MacBook; mac 13.4.0)'
        }


class VMAHeaders:
    def getHeaders(self):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '1024',
            'Accept': '*/*',
            'Host': Constants.VMAConstants.HEADER_HOST,
            'User-Agent': Constants.VMAConstants.HEADER_USER_AGENT
        }


class OTTHeaders:
    def getHeaders(self):
        return {
            'HOST': Constants.OTTConstants.HEADER_HOST,
            'APP': Constants.OTTConstants.HEADER_KEY
        }
