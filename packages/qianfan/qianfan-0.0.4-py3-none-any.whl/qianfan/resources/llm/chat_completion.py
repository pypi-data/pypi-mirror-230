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


from typing import Optional
from qianfan.consts import DefaultLLMModel
from qianfan.config import GLOBAL_CONFIG
from qianfan.resources.typing import QfLLMInfo, QfResponse, QfMessages
from qianfan.resources.llm.base import BaseResource, UNSPECIFIED_MODEL


class ChatCompletion(BaseResource):
    """
    QianFan ChatCompletion API Resource

    QianFan ChatCompletion is an agent for calling QianFan ChatCompletion API.

    """

    def _supported_models(self):
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
            "ERNIE-Bot-turbo": QfLLMInfo(
                endpoint="/chat/eb-instant",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "temperature",
                    "top_p",
                    "penalty_score",
                    "user_id",
                },
            ),
            "ERNIE-Bot": QfLLMInfo(
                endpoint="/chat/completions",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "temperature",
                    "top_p",
                    "penalty_score",
                    "user_id",
                },
            ),
            "BLOOMZ-7B": QfLLMInfo(
                endpoint="/chat/bloomz_7b1",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "Llama-2-7b-chat": QfLLMInfo(
                endpoint="/chat/llama_2_7b",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "Llama-2-13b-chat": QfLLMInfo(
                endpoint="/chat/llama_2_13b",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "Llama-2-70b-chat": QfLLMInfo(
                endpoint="/chat/llama_2_70b",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "Qianfan-BLOOMZ-7B-compressed": QfLLMInfo(
                endpoint="/chat/qianfan_bloomz_7b_compressed",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "Qianfan-Chinese-Llama-2-7B": QfLLMInfo(
                endpoint="/chat/qianfan_chinese_llama_2_7b",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "ChatGLM2-6B-32K": QfLLMInfo(
                endpoint="/chat/chatglm2_6b_32k",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            "AquilaChat-7B": QfLLMInfo(
                endpoint="/chat/aquilachat_7b",
                required_keys={"messages"},
                optional_keys={
                    "stream",
                    "user_id",
                },
            ),
            UNSPECIFIED_MODEL: QfLLMInfo(
                endpoint="",
                required_keys={"messages"},
                optional_keys={},
            ),
        }

    def _default_model(self):
        """
        default model of ChatCompletion `ERNIE-Bot-turbo`

        Args:
            None

        Returns:
           "ERNIE-Bot-turbo"

        """
        return DefaultLLMModel.ChatCompletion

    def _convert_endpoint(self, endpoint: str) -> str:
        """
        convert endpoint to ChatCompletion API endpoint
        """
        return f"/chat/{endpoint}"

    def do(
        self,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        stream: bool = False,
        retry_count: int = 1,
        request_timeout: float = 60,
        backoff_factor: float = 0,
        **kwargs,
    ) -> QfResponse:
        """
        if model is EB, use EB SDK to deal with the request
        """
        if "messages" in kwargs and isinstance(kwargs["messages"], QfMessages):
            kwargs["messages"] = kwargs["messages"]._to_list()
        if not GLOBAL_CONFIG.DISABLE_EB_SDK:
            if model in ["ERNIE-Bot-turbo", "ERNIE-Bot"]:
                import erniebot

                erniebot.ak = self._client._auth._ak
                erniebot.sk = self._client._auth._sk
                erniebot.access_token = self._client._auth.access_token()
                # compat with eb sdk
                if model == "ERNIE-Bot":
                    model = "ernie-bot-3.5"
                return erniebot.ChatCompletion.create(
                    model=model.lower(), messages=kwargs["messages"], stream=stream
                )
        return super().do(
            model,
            endpoint,
            stream,
            retry_count,
            request_timeout,
            backoff_factor,
            **kwargs,
        )

    async def ado(
        self,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        stream: bool = False,
        retry_count: int = 1,
        request_timeout: float = 60,
        backoff_factor: float = 0,
        **kwargs,
    ):
        """
        if model is EB, use EB SDK to deal with the request
        """
        if "messages" in kwargs and isinstance(kwargs["messages"], QfMessages):
            kwargs["messages"] = kwargs["messages"]._to_list()
        if not GLOBAL_CONFIG.DISABLE_EB_SDK:
            if model in ["ERNIE-Bot-turbo", "ERNIE-Bot"]:
                import erniebot

                erniebot.ak = self._client._auth._ak
                erniebot.sk = self._client._auth._sk
                erniebot.access_token = self._client._auth.access_token()
                # compat with eb sdk
                if model == "ERNIE-Bot":
                    model = "ernie-bot-3.5"
                return await erniebot.ChatCompletion.acreate(
                    model=model.lower(), messages=kwargs["messages"], stream=stream
                )
        return await super().ado(
            model,
            endpoint,
            stream,
            retry_count,
            request_timeout,
            backoff_factor,
            **kwargs,
        )
