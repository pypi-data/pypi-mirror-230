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

from typing import Any, ClassVar, Dict, Optional, Tuple, Union, Iterator, AsyncIterator
from collections import defaultdict

import erniebot
import qianfan.errors as errors
import erniebot.types as ebtypes
from erniebot.response import EBResponse

from qianfan.resources.base import BaseResource
from qianfan.utils import log_info, _set_val_if_key_exists

QIANFAN_DEFAULT_CHAT_COMPLETION_MODEL = "ERNIE-Bot-turbo"


class ChatCompletion(BaseResource):
    """
    QianFan ChatCompletion API Resource

    QianFan ChatCompletion is an agent for calling QianFan ChatCompletion API.

    """

    def __init__(self, **kwargs: Any) -> None:
        """
        init Qianfan ChatCompletion

        Args:
            **kwargs (Any): ak, sk

        Returns:
            None

        """
        super().__init__(**kwargs)

    def do(cls, **kwargs: Any) -> Union[EBResponse, Iterator[EBResponse]]:
        """
        Create chat completion request

        Args:
            **kwargs (dict):
                model: qianfan completion model
                endpoint: completion api endpoint

        Returns:
            EBResponse: completion response

        """
        kwargs["endpoint"] = cls._get_endpoint_from_dict(**kwargs)
        return QfChatCompletionAPIResource.create(**kwargs)

    async def ado(cls, **kwargs: Any) -> Union[EBResponse, AsyncIterator[EBResponse]]:
        """
        Async create chat completion request

        Args:
            **kwargs (dict):
                model: qianfan completion model
                endpoint: completion api endpoint

        Returns:
            EBResponse: completion response

        """
        kwargs["endpoint"] = cls._get_endpoint_from_dict(**kwargs)
        return await QfChatCompletionAPIResource.acreate(**kwargs)

    def _supported_model_endpoint(self):
        """
        preset model list of ChatCompletion
        support model:
         - ERNIE-Bot-turbo
         - ERNIE-Bot
         - BLOOMZ-7B
         - Llama-2-7b-chat
         - Llama-2-13b-chat
         - Llama-2-70b-chat
         - Qianfan-BLOOMZ-7B-compressed
         - Qianfan-Chinese-Llama-2-7B
         - ChatGLM2-6B-32K
         - AquilaChat-7B

        Args:
            None

        Returns:
            a dict which key is preset model and value is the endpoint

        """
        return {
            "ERNIE-Bot-turbo": "eb-instant",
            "ERNIE-Bot": "completions",
            "BLOOMZ-7B": "bloomz_7b1",
            "Llama-2-7b-chat": "llama_2_7b",
            "Llama-2-13b-chat": "llama_2_13b",
            "Llama-2-70b-chat": "llama_2_70b",
            "Qianfan-BLOOMZ-7B-compressed": "qianfan_bloomz_7b_compressed",
            "Qianfan-Chinese-Llama-2-7B": "qianfan_chinese_llama_2_7b",
            "ChatGLM2-6B-32K": "chatglm2_6b_32k",
            "AquilaChat-7B": "aquilachat_7b",
        }

    def _default_model(self):
        """
        default model of ChatCompletion `ERNIE-Bot-turbo`

        Args:
            None

        Returns:
           "ERNIE-Bot-turbo"

        """
        return QIANFAN_DEFAULT_CHAT_COMPLETION_MODEL


class QfChatCompletionAPIResource(erniebot.ChatCompletion):
    """
    QianFan ChatCompletion Resource

    providing access to QianFan "chat" API.

    """

    # the prefix of the endpoint in "chat" qianfan url
    _URL_PREFIX = "chat"

    def __init__(self, **kwargs: Any) -> None:
        """
        Init QfChatCompletionAPIResource

        Args:
            None

        Returns:
            None

        """
        super().__init__()

    def _prepare_create(
        self, kwargs: Dict[str, Any]
    ) -> Tuple[
        str,
        Optional[ebtypes.ParamsType],
        Optional[ebtypes.HeadersType],
        Optional[ebtypes.FilesType],
        bool,
        Optional[float],
    ]:
        """
        Args:
            kwargs (Dict[str, Any]): `endpoint` and `input` are necessary

        Returns:
            Tuple[
                str,
                Optional[ParamsType],
                Optional[HeadersType],
                Optional[FilesType],
                bool,
                Optional[float]
            ]:

                * `url` (str): the url to be requested
                * `params` (Optional[ParamsType]): the params of the request
                * `headers` (Optional[HeadersType]): the header of the request
                * `files` (Optional[FilesType]): the files in the request
                * `stream` (bool): whether to enable stream response
                * `request_timeout` (Optional[float]): the timeout of the request

        Raises:
            ArgumentNotFoundError: thrown when endpoint or input is not found
        """

        REQUIRED_KEYS = {"endpoint", "messages"}
        for key in REQUIRED_KEYS:
            if key not in kwargs:
                raise errors.ArgumentNotFoundError(f"`{key}` is not found.")

        endpoint = kwargs["endpoint"]
        messages = kwargs["messages"]

        url = f"/{self._URL_PREFIX}/{endpoint}"

        log_info("requesting url: %s" % url)

        params = {}
        params["messages"] = messages
        _set_val_if_key_exists(kwargs, params, "stream")
        _set_val_if_key_exists(kwargs, params, "temperature")
        _set_val_if_key_exists(kwargs, params, "top_p")
        _set_val_if_key_exists(kwargs, params, "penalty_score")
        _set_val_if_key_exists(kwargs, params, "user_id")
        _set_val_if_key_exists(kwargs, params, "functions")

        headers = kwargs.get("headers", None)
        files = None
        stream = kwargs.get("stream", False)
        request_timeout = kwargs.get("request_timeout", None)

        return url, params, headers, files, stream, request_timeout
