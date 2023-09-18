# Copyright (c) 2023 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import threading

from typing import Dict, Tuple, Optional

from qianfan.utils.helper import Singleton
from qianfan.utils import _get_value_from_dict_or_var_or_env
from qianfan.utils import log_warn, log_info, log_error
from qianfan.config import GLOBAL_CONFIG
from qianfan.resources.http_client import HTTPClient
from qianfan.resources.typing import QfRequest, RetryConfig
from qianfan.errors import InvalidArgumentError, InternalError
from qianfan.consts import Env


class AuthManager(metaclass=Singleton):
    """
    AuthManager is singleton to manage all access token in SDK
    """

    class AccessToken:
        """
        Access Token object
        """

        token: Optional[str]
        lock: threading.Lock
        refresh_at: float

        def __init__(self, access_token=None):
            """
            Init access token object
            """
            self.token = access_token
            self.lock = threading.Lock()
            self.refresh_at = 0

    _token_map: Dict[Tuple[str, str], AccessToken]

    def __init__(self) -> None:
        """
        Init Auth manager
        """
        self._token_map = {}
        self._client = HTTPClient()
        self._lock = threading.Lock()

    def register(self, ak: str, sk: str, access_token: Optional[str] = None):
        """
        add `(ak, sk)` to manager and update access token
        """
        existed = True
        with self._lock:
            if (ak, sk) not in self._token_map:
                self._token_map[(ak, sk)] = AuthManager.AccessToken(access_token)
                existed = False

        if not existed and access_token is None:
            self.refresh_access_token(ak, sk)

    def get_access_token(self, ak: str, sk: str) -> str:
        """
        get access token by `(ak, sk)`
        """
        with self._lock:
            obj = self._token_map.get((ak, sk), None)
        if obj is None:
            raise InternalError("provided ak and sk are not registered")
        with obj.lock:
            if obj.token is None:
                log_warn("access token is not available")
                return ""
            return obj.token

    def refresh_access_token(self, ak: str, sk: str):
        """
        refresh access token of `(ak, sk)`
        """
        with self._lock:
            obj = self._token_map.get((ak, sk), None)
        if obj is None:
            raise InternalError("provided ak and sk are not register")
        with obj.lock:
            log_info("trying to refresh access_token")
            if time.time() - obj.refresh_at < 60 * 60:
                # in case multiple threads try to refresh at the same time, the token will
                # be refreshed multiple times
                log_info("access_token is already refreshed, skip refresh.")
                return
            try:
                resp = self._client.request(
                    QfRequest(
                        method="POST",
                        url="{}{}".format(
                            GLOBAL_CONFIG.BASE_URL, GLOBAL_CONFIG.AUTH_URL
                        ),
                        query={
                            "grant_type": "client_credentials",
                            "client_id": ak,
                            "client_secret": sk,
                        },
                        retry_config=RetryConfig(timeout=GLOBAL_CONFIG.AUTH_TIMEOUT),
                    )
                )
                resp = resp.json()
                if "error" in resp:
                    log_error(
                        "refresh access_token failed, error description={}".format(
                            resp["error_description"]
                        )
                    )
                    return
                obj.token = resp["access_token"]
                obj.refresh_at = time.time()
            except Exception as e:
                log_error(f"refresh access token failed with exception {str(e)}")
                return

        log_info("sucessfully refresh access_token")


class Auth(object):
    """
    object to maintain acccess token for api call
    """

    def __init__(self, **kwargs) -> None:
        """
        recv `ak`, `sk` and `access_token` from kwargs
        if the args does not contain the arguments, env variable will be used

        when `ak` and `sk` are provided, `access_token` will be set automatically
        """
        self._ak = _get_value_from_dict_or_var_or_env(
            kwargs, "ak", GLOBAL_CONFIG.AK, Env.AK
        )
        self._sk = _get_value_from_dict_or_var_or_env(
            kwargs, "sk", GLOBAL_CONFIG.SK, Env.SK
        )
        self._access_token = _get_value_from_dict_or_var_or_env(
            kwargs, "access_token", GLOBAL_CONFIG.ACCESS_TOKEN, Env.AccessToken
        )
        if self._access_token is None:
            if self._ak is None or self._sk is None:
                raise InvalidArgumentError(
                    "both ak and sk must be provided, otherwise access_token should be provided"
                )
            AuthManager().register(self._ak, self._sk, self._access_token)
        else:
            if not (self._ak is None or self._sk is None):
                AuthManager().register(self._ak, self._sk, self._access_token)

    def refresh_access_token(self) -> None:
        """
        refresh `access_token` using `ak` and `sk`
        """
        if self._ak is None or self._sk is None:
            log_warn("AK or SK is not set, refresh access_token will not work.")
            return
        AuthManager().refresh_access_token(self._ak, self._sk)

    def access_token(self) -> str:
        """
        get current `access_token`
        """
        if self._ak is None or self._sk is None:
            if self._access_token is None:
                log_warn("Access token is not available! Please check code!")
                return ""
            return self._access_token
        return AuthManager().get_access_token(self._ak, self._sk)
