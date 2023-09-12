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

from typing import Any, ClassVar, Dict, Optional, Tuple
from collections import defaultdict
import types

import qianfan.errors as errors
from erniebot.types import FilesType, HeadersType, ParamsType
from erniebot.response import EBResponse
from erniebot.resources.abc.creatable import Creatable
from erniebot.resources.resource import EBResource

from qianfan.resources.base import BaseResource
from qianfan.utils import log_info, _set_val_if_key_exists
from qianfan.resources.chat_completion import (
    ChatCompletion,
    QfChatCompletionAPIResource,
)

QIANFAN_DEFAULT_COMPLETION_MODEL = "ERNIE-Bot-turbo"


class Completion(BaseResource):
    """
    QianFan Completion API Resource

    QianFan Completion is an agent for calling QianFan completion API.

    """

    def __init__(self, **kwargs: Any) -> None:
        """
        init Qianfan Completion

        Args:
            **kwargs (Any): ak, sk

        Returns:
            None

        """
        super().__init__(**kwargs)
        if "endpoint" in kwargs:
            self._endpoint = f"/{QfCompletionAPIResource._URL_PREFIX}/{self._endpoint}"

    def _preprocess(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        preprocess before send request
        """
        if "endpoint" in kwargs:
            endpoint = kwargs["endpoint"]
            return f"/{QfCompletionAPIResource._URL_PREFIX}/{endpoint}"
        if "model" in kwargs:
            return self._get_endpoint(kwargs["model"])
        return self._endpoint

    def do(self, **kwargs: Any):
        """
        Create completion request

        Args:
            **kwargs (dict):
                model: qianfan completion model
                endpoint: completion api endpoint

        Returns:
            EBResponse: completion response

        """
        kwargs["endpoint"] = self._preprocess(**kwargs)
        return QfCompletionAPIResource.create(**kwargs)

    async def ado(self, **kwargs: Any):
        """
        Async create completion request

        Args:
            **kwargs (dict):
                model: qianfan completion model
                endpoint: completion api endpoint

        Returns:
            EBResponse: completion response

        """
        kwargs["endpoint"] = self._preprocess(**kwargs)
        return await QfCompletionAPIResource.acreate(**kwargs)

    def _supported_model_endpoint(self):
        """
        preset model list of Completions
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
            "ERNIE-Bot-turbo": "/chat/eb-instant",
            "ERNIE-Bot": "/chat/completions",
            "BLOOMZ-7B": "/chat/bloomz_7b1",
            "Llama-2-7b-chat": "/chat/llama_2_7b",
            "Llama-2-13b-chat": "/chat/llama_2_13b",
            "Llama-2-70b-chat": "/chat/llama_2_70b",
            "Qianfan-BLOOMZ-7B-compressed": "/chat/qianfan_bloomz_7b_compressed",
            "Qianfan-Chinese-Llama-2-7B": "/chat/qianfan_chinese_llama_2_7b",
            "ChatGLM2-6B-32K": "/chat/chatglm2_6b_32k",
            "AquilaChat-7B": "/chat/aquilachat_7b",
        }

    def _default_model(self):
        """
        default model of Completion: ERNIE-Bot-turbo

        Args:
            None

        Returns:
           ERNIE-Bot-turbo

        """
        return QIANFAN_DEFAULT_COMPLETION_MODEL


class QfCompletionAPIResource(EBResource, Creatable):
    """
    QianFan Completion API Resource

    providing access to QianFan "completions" API.

    """

    # the prefix of the endpoint in "completions" qianfan url
    _URL_PREFIX = "completions"

    def _prepare_create(
        self, kwargs: Dict[str, Any]
    ) -> Tuple[
        str,
        Optional[ParamsType],
        Optional[HeadersType],
        Optional[FilesType],
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
            QianfanError: will be thrown when kwargs include unexpected key or do not include the required key
        """
        REQUIRED_KEYS = {"endpoint", "prompt"}
        for key in REQUIRED_KEYS:
            if key not in kwargs or kwargs[key] is None:
                raise errors.ArgumentNotFoundError(f"Missing required key: {key}")

        prompt = kwargs["prompt"]

        params = {"prompt": prompt}
        if "user_id" in kwargs:
            params["user_id"] = kwargs["user_id"]

        headers = kwargs.get("headers", None)
        files = None
        stream = kwargs.get("stream", False)
        request_timeout = kwargs.get("request_timeout", None)

        if kwargs["endpoint"][1:].startswith("chat"):
            # is using chat to simulate completion
            params["messages"] = [{"role": "user", "content": prompt}]
            del params["prompt"]
        url = kwargs["endpoint"]
        log_info("requesting url: %s" % url)

        _set_val_if_key_exists(kwargs, params, "stream")
        _set_val_if_key_exists(kwargs, params, "temperature")
        _set_val_if_key_exists(kwargs, params, "top_p")
        _set_val_if_key_exists(kwargs, params, "penalty_score")
        _set_val_if_key_exists(kwargs, params, "user_id")
        _set_val_if_key_exists(kwargs, params, "functions")

        return url, params, headers, files, stream, request_timeout

    def _post_process_create(self, resp):
        """
        This is the function invoked after request the api.
        In order to mock completions with chat api, we need to change the `object`
        in response from "chat.completion" to "completion".

        `resp` could be EBResponse, Generator(stream) or AsyncGenerator(async stream)
        Since we need to keep the return value type and also change the generated value,
        use Wrapper to change the Generator.
        """

        class GeneratorWrapper:
            """
            wrapper for Generator
            """

            def __init__(self, source) -> None:
                """
                source is the original generator
                """
                self.source = source

            def __iter__(self):
                """
                self is the iterator, return self
                """
                return self

            def __next__(self):
                """
                magic method of iterator
                """
                return self.next()

            def next(self):
                """
                get the value from original generator
                modify the "object" in value
                and return
                """
                value = self.source.__next__()
                value.__setstate__({"object": "completion"})
                return value

        class AsyncGeneratorWrapper:
            """
            wrapper for AsyncGenerator
            """

            def __init__(self, source):
                """
                source is the original async generator
                """
                self.source = source

            def __aiter__(self):
                """
                self is the iterator, return self
                """
                return self

            async def __anext__(self):
                return await self.anext()

            async def anext(self):
                """
                get the value from original generator
                modify the "object" in value
                and return
                """
                value = await self.source.__anext__()
                value.__setstate__({"object": "completion"})
                return value

        # resp could be EBResponse, Generator(stream) or AsyncGenerator(async stream)
        # when it's EBResponse, means that it's not stream
        if isinstance(resp, EBResponse):
            resp.__setstate__({"object": "completion"})
            return resp
        # when it's async stream, resp would be AsyncGenerator
        # use wrapper to change the generated value
        elif isinstance(resp, types.AsyncGeneratorType):
            return AsyncGeneratorWrapper(resp)
        # when it's sync stream, resp would be Generator
        elif isinstance(resp, types.GeneratorType):
            return GeneratorWrapper(resp)

        return resp
