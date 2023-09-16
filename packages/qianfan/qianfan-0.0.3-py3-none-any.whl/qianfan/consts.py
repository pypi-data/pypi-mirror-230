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

"""
Consts used in qianfan sdk
"""

import enum
from typing import Optional


class APIErrorCode(enum.Enum):
    """
    Error code from API return value
    """

    NoError = 0
    UnknownError = 1
    ServiceUnavailable = 2
    UnsupportedMethod = 3
    RequestLimitReached = 4
    NoPermissionToAccessData = 6
    GetServiceTokenFailed = 13
    AppNotExist = 15
    DailyLimitReached = 17
    QPSLimitReached = 18
    TotalRequestLimitReached = 19
    InvalidRequest = 100
    APITokenInvalid = 110
    APITokenExpired = 111
    InternalError = 336000
    InvalidArgument = 336001
    InvalidJSON = 336002
    InvalidParam = 336003
    PermissionError = 336004
    APINameNotExist = 336005
    ServerHighLoad = 336100
    InvalidHTTPMethod = 336101


class Env:
    """
    Environment variable name used by qianfan sdk
    """

    AK: str = "QIANFAN_AK"
    SK: str = "QIANFAN_SK"
    AccessToken: str = "QIANFAN_ACCESS_TOKEN"
    BaseURL: str = "QIANFAN_BASE_URL"
    ModelAPIPrefix: str = "QIANFAN_MODEL_API_PREFIX"
    AuthAPIPrefix: str = "QIANFAN_AUTH_API_PREFIX"
    DisableErnieBotSDK: str = "QIANFAN_DISABLE_EB_SDK"
    AuthTimeout: str = "QIANFAN_AUTH_TIMEOUT"


class DefaultValue:
    """
    Default value used by qianfan sdk
    """

    AK: Optional[str] = None
    SK: Optional[str] = None
    AccessToken: Optional[str] = None
    BaseURL: str = "https://aip.baidubce.com"
    ModelAPIPrefix: str = "/rpc/2.0/ai_custom/v1/wenxinworkshop"
    AuthAPIPrefix: str = "/oauth/2.0/token"
    AuthTimeout: int = 5
    DisableErnieBotSDK: bool = False


class DefaultLLMModel:
    """
    Defualt LLM model in qianfan sdk
    """

    Completion = "ERNIE-Bot-turbo"
    ChatCompletion = "ERNIE-Bot-turbo"
    Embedding = "Embedding-V1"
