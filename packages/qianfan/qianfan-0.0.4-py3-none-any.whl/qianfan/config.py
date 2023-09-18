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

from qianfan.consts import Env, DefaultValue
from qianfan.utils import _get_from_env_or_default
from qianfan.utils.helper import Singleton
from typing import Optional


class GlobalConfig(object, metaclass=Singleton):
    """
    The global config of whole qianfan sdk
    """

    AK: Optional[str]
    SK: Optional[str]
    ACCESS_TOKEN: Optional[str]
    BASE_URL: str
    MODEL_API_PREFIX: str
    AUTH_URL: str
    AUTH_TIMEOUT: int
    DISABLE_EB_SDK: bool

    def __init__(self) -> None:
        """
        Read value from environment or the default value will be used
        """
        self.BASE_URL = _get_from_env_or_default(Env.BaseURL, DefaultValue.BaseURL)
        self.MODEL_API_PREFIX = _get_from_env_or_default(
            Env.ModelAPIPrefix, DefaultValue.ModelAPIPrefix
        )
        self.AUTH_URL = _get_from_env_or_default(
            Env.AuthAPIPrefix, DefaultValue.AuthAPIPrefix
        )
        self.AUTH_TIMEOUT = int(
            _get_from_env_or_default(Env.AuthTimeout, str(DefaultValue.AuthTimeout))
        )
        self.DISABLE_EB_SDK = _get_from_env_or_default(
            Env.DisableErnieBotSDK, DefaultValue.DisableErnieBotSDK
        )
        self.AK = _get_from_env_or_default(Env.AK, DefaultValue.AK)
        self.SK = _get_from_env_or_default(Env.SK, DefaultValue.SK)
        self.ACCESS_TOKEN = _get_from_env_or_default(
            Env.AccessToken, DefaultValue.AccessToken
        )


GLOBAL_CONFIG = GlobalConfig()


def AK(ak: str) -> None:
    """
    set global AK
    """
    GLOBAL_CONFIG.AK = ak


def SK(sk: str) -> None:
    """
    set global SK
    """
    GLOBAL_CONFIG.SK = sk


def AccessToken(access_token: str) -> None:
    """
    set global AccessToken
    """
    GLOBAL_CONFIG.ACCESS_TOKEN = access_token
