import random


class Payloads:
    def enroll_payload(self, **kwargs):
        body = \
            dict(enterpriseId='', userId='', deviceId='device12340', deviceName='Google', deviceType='Android',
                 deviceMake='Google', deviceModel='Android 12', osVersion='12', appName='UCaaS',
                 pushId='faebeb194a2e8b1ad3f7fc9575')
        body.update(kwargs)
        return body

    def employee_payload(self, **kwargs):
        body = dict(name='', salary='', age='')
        body.update(kwargs)
        return body

    def create_post_payload(self, **kwargs):
        body = dict(title='', body='', userId=random.randint(0, 100))
        body.update(kwargs)
        return body

    def comments_by_post_id_payload(self, **kwargs):
        body = dict(postId='')
        body.update(kwargs)
        return body


class VMAPayloads:
    def get_provisioning_payload(self, **kwargs):
        body = \
            dict(mdn='', deviceId='', loginToken='')
        body.update(kwargs)
        return body
