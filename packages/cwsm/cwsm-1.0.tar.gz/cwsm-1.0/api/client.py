# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import time
from requests.models import PreparedRequest
from cwps_sm import SM4

from api.http import http_post, http_get, http_put, http_delete

logger = logging.getLogger("cwsm")


class Client(object):
    """
    input: json
    """

    def __init__(self, app_code=None, cwsm_host=None, bk_token=None, bk_username=None, app_secret=None):
        """
        - 用户态的用法: Client(app_code, bk_token, cwsm_host)
        - 非用户态的用法: Client(app_code, username, app_secret, cwsm_host)
        """

        self._app_code = app_code
        self._host = cwsm_host
        self._bk_token = bk_token
        self._bk_username = bk_username
        self._app_secret = app_secret

        is_api_debug_enabled = (os.environ.get("CWSM_API_DEBUG") == "true"
                                or os.environ.get("BKAPP_CWSM_API_DEBUG") == "true")
        is_api_force_enabled = (os.environ.get("CWSM_API_FORCE") == "true"
                                or os.environ.get("BKAPP_CWSM_API_FORCE") == "true")

        self._extra_url_params = {}
        if is_api_debug_enabled:
            self._extra_url_params["debug"] = "true"
        if is_api_force_enabled:
            self._extra_url_params["force"] = "true"


    def _call_api(self, http_func, path, data, headers=None, cookie=None, params=None, timeout=None):
        url = "{host}{path}".format(host=self._host, path=path)

        begin = time.time()

        # add extra params in url if not empty
        if self._extra_url_params:
            preReq = PreparedRequest()
            preReq.prepare_url(url, self._extra_url_params)
            url = preReq.url
        app_secret = self._app_secret
        # 添加sm4加密操作
        # key可以是长度不超过16的任意值
        key = app_secret[:16]
        byte_key = key.encode('utf-8')
        sm4 = SM4(byte_key,mode=SM4.Mode.ECB)
        # CBC模式需要初始向量IV，iv参数默认为b'0000000000000000'
        # sm4 = SM4(byte_key, mode=SM4.Mode.CBC, iv=byte_key)
        data, err = sm4.encrypt(json.dumps(data))
        length = len(data)
        print(length,":",data)
        # text, err = sm4.decrypt(data)
        # print(text)
        ok, message, _data = http_func(url, data, headers=headers, cookies=cookie, timeout=timeout)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("do http request: method=`%s`, url=`%s`, data=`%s`", http_func.__name__, url, json.dumps(data))
            logger.debug("http request result: ok=`%s`, message=`%s`, _data=`%s`", ok, message, json.dumps(_data))
            logger.debug("http request took %s ms", int((time.time() - begin) * 1000))

        if not ok:
            return False, message or "request to cwsm server fail", None

        if _data.get("code") != 0:
            return False, _data.get("message") or "cwsm api fail", None

        _d = _data.get("data")
        # sm4 解密操作
        # print(len(_d),_d)
        # result, err = sm4.decrypt(json.dumps(_d))
        # print(result)

        return True, "ok", _d

    def _call_cwsm_api(self, http_func, path, data, params=None, timeout=None):
        """
        调用 cwsm api
        优先适配用户态的方式
        """
        
        cookie = {}
        headers = {}
        if len(self._bk_token) > 0:
            cookie["bk_token"] = self._bk_token
            headers = {
                "X-SDK-Key": "SDKRequest",
            }
        elif (self._bk_username != '') & (self._app_secret != ''):
            headers = {
                "X-Bk-App-Secret": self._app_secret,
                "X-Bk-Username": self._bk_username,
                "X-SDK-Key": "SDKRequest",
            }
        else:
            return False, "the authentication information cannot be empty. (bk_token) or (username + app_secret) " \
                          "must be entered", None
        
        return self._call_api(http_func, path, data, headers, cookie=cookie, params=params, timeout=timeout)

    # 创建凭据
    def add_secrets(self, data):
        path = "/api/app/{app_id}/secrets/".format(app_id=self._app_code)
        ok, message, data = self._call_cwsm_api(http_post, path, data)
        return ok, message

    # 凭据列表
    def secrets_list(self, params):
        path = "/api/app/{app_id}/secrets/".format(app_id=self._app_code)
        ok, message, data = self._call_cwsm_api(http_get, path, params)
        return ok, message

    # 更新凭据
    def update_secrets(self, secrets_key, data):
        path = "/api/app/{app_id}/secrets/{secrets_key}/".format(app_id=self._app_code, secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_put, path, data)
        return ok, message

    # 凭据详情
    def get_secrets(self, secrets_key):
        path = "/api/app/{app_id}/secrets/{secrets_key}/".format(app_id=self._app_code, secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_get, path, {})
        return ok, message, data

    # 删除凭据
    def del_secrets(self, secrets_key):
        path = "/api/app/{app_id}/secrets/{secrets_key}/".format(app_id=self._app_code, secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_delete, path, data={})
        return ok, message

    def share_secrets(self, secrets_key, data):
        path = "/api/app/{app_id}/secrets/{secrets_key}/share/".format(app_id=self._app_code, secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_post, path, data)
        return ok, message

    # 取消凭据共享
    def unshare_secrets(self, secrets_key, data):
        path = "/api/app/{app_id}/secrets/{secrets_key}/unshare/".format(app_id=self._app_code, secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_delete, path, data)
        return ok, message

    def secrets_auth_users(self, secrets_key, data):
        path = "/api/app/{app_id}/secrets/{secrets_key}/auth_users/".format(app_id=self._app_code,
                                                                            secrets_key=secrets_key)
        ok, message, data = self._call_cwsm_api(http_get, path, data)
        return ok, message, data

    def tag_list(self, params):
        path = "/api/app/{app_id}/tag/list/".format(app_id=self._app_code)
        ok, message, data = self._call_cwsm_api(http_get, path, params)
        return ok, message, data

    def unbind_secrets_tag(self, tag_key, tag_value, secrets_key, data):
        path = "/api/app/{app_id}/tag/{tag_key}/{tag_value}/unbind/{secrets_key}/".format(
            app_id=self._app_code,
            tag_key=tag_key,
            tag_value=tag_value,
            secrets_key=secrets_key
        )
        ok, message, data = self._call_cwsm_api(http_delete, path, data)
        return ok, message
    
    # 批量创建或更新凭据
    def batch_create_or_update_secrets(self, data):
        path = "/api/app/{app_id}/secrets/batch_update_or_create/".format(app_id = self._app_code)
        ok,message,data =  self._call_cwsm_api(http_post,path,data)
        return ok,message,data
    
    # 批量删除凭据
    def batch_del_secrets(self, data):
        path = "/api/app/{app_id}/secrets/batch_del/".format(app_id = self._app_code)
        ok,message,data =  self._call_cwsm_api(http_post,path,data)
        return ok,message,data

    # 查询绑定了标签的所有凭据 TODO
    def get_bind_tag_secret_list(self,app_key,tag_key):
        path = "/api/app/{app_id}/tag/{tag_key}/bind_secrets/list/".format(app_id=app_key,tag_key=tag_key)
        ok,message,data = self._call_cwsm_api(http_get,path)
        return ok,message,data
    
    # 查询当前应用下存在的凭据key列表 TODO
    def get_secret_key_list(self,app_key):
        path = "/api/app/{app_id}/secrets/secrets_key_list/".format(app_key=app_key)
        ok,message,data = self._call_cwsm_api(http_get,path)
        return ok,message,data