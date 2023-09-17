import logging
from api.client import Client

logger = logging.getLogger("cwsm")


class CWSM(object):
    """
    input: object
    """

    def __init__(self, app_code, cwsm_host, bk_token=None, bk_username=None, app_secret=None, ):
        """
        - 没有APIGateway的用法: IAM(app_code, app_secret, bk_iam_host, bk_paas_host)
        - 有APIGateway的用法: IAM(app_code, app_secret, bk_apigateway_url)
        """
        self._client = Client(app_code, cwsm_host, bk_token, bk_username, app_secret)

    def add_secrets(self, data):
        return self._client.add_secrets(data=data)

    def secrets_list(self, params):
        return self._client.secrets_list(params=params)

    def update_secrets(self, secrets_key, data):
        return self._client.update_secrets(secrets_key=secrets_key, data=data)

    def get_secrets(self, secrets_key):
        return self._client.get_secrets(secrets_key=secrets_key)

    def del_secrets(self, secrets_key):
        return self._client.del_secrets(secrets_key)

    def share_secrets(self, secrets_key, data):
        return self._client.share_secrets(secrets_key=secrets_key, data=data)

    def unshare_secrets(self, secrets_key, data):
        return self._client.unshare_secrets(secrets_key=secrets_key, data=data)

    def secrets_auth_users(self, secrets_key, data):
        return self._client.secrets_auth_users(secrets_key=secrets_key, data=data)

    def tag_list(self, params):
        return self._client.tag_list(params=params)

    def unbind_secrets_tag(self, tag_key, tag_value, secrets_key, data):
        return self._client.unbind_secrets_tag(tag_key=tag_key, tag_value=tag_value, secrets_key=secrets_key, data=data)

    def batch_create_or_update_secrets(self, data):
        return self._client.batch_create_or_update_secrets(data=data)
    
    def batch_del_secrets(self, data):
        return self._client.batch_del_secrets(data=data)
    
    def get_bind_tag_secret_list(self,app_Key,tag_Key):
        return self._client.get_bind_tag_secret_list(app_Key=app_Key,tag_Key=tag_Key)
    
    def get_secret_key_list(self,app_key):
        return self._client.get_secret_key_list(app_key=app_key)