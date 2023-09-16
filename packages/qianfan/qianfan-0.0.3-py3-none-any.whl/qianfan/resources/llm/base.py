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

import copy
from typing import Any, Dict, Optional, Set

import qianfan.errors as errors
from qianfan.utils import log_warn
from qianfan.resources.client import QfClient
from qianfan.resources.typing import QfResponse, QfLLMInfo, JsonBody, RetryConfig

# This is used when user provides `endpoint`
# In such cases, SDK cannot know which model the user is using
# This constant is used to express no model is spcified,
# so that SDK still can get the requirements of API from _supported_models()
UNSPECIFIED_MODEL = "UNSPECIFIED_MODEL"


class BaseResource(object):
    """
    base class of Qianfan object
    """

    def __init__(
        self,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        init resource

        """
        self._client = QfClient(**kwargs)
        if endpoint is not None:
            self._endpoint = self._convert_endpoint(endpoint)
        else:
            model = model if model is not None else self._default_model()
            self._endpoint = self._supported_models()[model].endpoint

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
        qianfan resource basic do

        Args:
            **kwargs (dict): kv dict data。

        """
        self._check_params(
            model,
            endpoint,
            stream,
            retry_count,
            request_timeout,
            backoff_factor,
            **kwargs,
        )
        retry_config = RetryConfig(
            retry_count=retry_count,
            timeout=request_timeout,
            backoff_factor=backoff_factor,
        )
        endpoint = self._get_endpoint_from_dict(model, endpoint, stream, **kwargs)
        resp = self._client.llm(
            endpoint=endpoint,
            header=self._generate_header(model, endpoint, stream, **kwargs),
            query=self._generate_query(model, endpoint, stream, **kwargs),
            body=self._generate_body(model, endpoint, stream, **kwargs),
            stream=stream,
            data_postprocess=self._data_postprocess,
            retry_config=retry_config,
        )
        return resp

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
        qianfan aio resource basic do

        Args:
            **kwargs: kv dict data

        Returns:
            None

        """
        self._check_params(
            model,
            endpoint,
            stream,
            retry_count,
            request_timeout,
            backoff_factor,
            **kwargs,
        )
        retry_config = RetryConfig(
            retry_count=retry_count,
            timeout=request_timeout,
            backoff_factor=backoff_factor,
        )
        endpoint = self._get_endpoint_from_dict(model, endpoint, stream, **kwargs)
        resp = await self._client.async_llm(
            endpoint=endpoint,
            header=self._generate_header(model, endpoint, stream, **kwargs),
            query=self._generate_query(model, endpoint, stream, **kwargs),
            body=self._generate_body(model, endpoint, stream, **kwargs),
            stream=stream,
            data_postprocess=self._data_postprocess,
            retry_config=retry_config,
        )
        return resp

    def _check_params(
        self,
        model: Optional[str],
        endpoint: Optional[str],
        stream: bool,
        retry_count: int,
        request_timeout: float,
        backoff_factor: float,
        **kwargs,
    ):
        """
        check user provide params
        """
        if stream is True and retry_count != 1:
            raise errors.InvalidArgumentError(
                "retry is not available when stream is enabled"
            )

    def _supported_models(self) -> Dict[str, QfLLMInfo]:
        """
        preset model list

        Args:
            None

        Returns:
            a dict which key is preset model and value is the endpoint

        """
        raise NotImplementedError

    def _default_model(self) -> str:
        """
        default model

        Args:
            None

        Return:
            a str which is the default model name
        """
        raise NotImplementedError

    def _get_endpoint(self, model: str) -> QfLLMInfo:
        """
        get the endpoint of the given `model`

        Args:
            model (str): the name of the model, must be defined in _SUPPORTED_MODEL_ENDPOINTS

        Returns:
            str: the endpoint of the input `model`

        Raises:
            QianfanError: if the input is not in _SUPPORTED_MODEL_ENDPOINTS
        """
        if model not in self._supported_models():
            raise errors.InvalidArgumentError(
                f"The provided model `{model}` is not in the list of supported models. "
                f"If this is a recently added model, try using the `endpoint` arguments "
                f"and create an issue to tell us. Supported models: {self.models()}"
            )
        return self._supported_models()[model]

    def _get_endpoint_from_dict(
        self, model: Optional[str], endpoint: Optional[str], stream: bool, **kwargs
    ) -> str:
        """
        extract the endpoint of the model in kwargs, or use the endpoint defined in __init__

        Args:
            **kwargs (dict): any dict

        Returns:
            str: the endpoint of the model in kwargs

        """
        if endpoint is not None:
            return self._convert_endpoint(endpoint)
        if model is not None:
            return self._get_endpoint(model).endpoint
        return self._endpoint

    def _generate_header(
        self, model: Optional[str], endpoint: str, stream: bool, **kwargs: Any
    ) -> JsonBody:
        """
        generate header
        """
        if "header" in kwargs:
            return kwargs["header"]
        return {}

    def _generate_query(
        self, model: Optional[str], endpoint: str, stream: bool, **kwargs: Any
    ) -> JsonBody:
        """
        generate query
        """
        if "query" in kwargs:
            return kwargs["query"]
        return {}

    def _generate_body(
        self, model: Optional[str], endpoint: str, stream: bool, **kwargs: Any
    ) -> JsonBody:
        """
        generate body
        """
        kwargs = copy.deepcopy(kwargs)
        IGNORED_KEYS = {"headers", "query"}
        for key in IGNORED_KEYS:
            if key in kwargs:
                del kwargs[key]
        if model is not None:
            # is preset model
            if model not in self._supported_models():
                raise errors.InvalidArgumentError(
                    f"The provided model `{model}` is not in the list of supported models. "
                    f"If this is a recently added model, try using the `endpoint` arguments "
                    f"and create an issue to tell us. Supported models: {self.models()}"
                )
            model_info = self._supported_models()[model]
            # warn if user provide unexpected arguments
            for key in kwargs:
                if (
                    key not in model_info.required_keys
                    and key not in model_info.optional_keys
                ):
                    log_warn(
                        f"This key `{key}` does not seem to be a parameter that the model `{model}` will accept"
                    )
        else:
            default_model_info = self._supported_models()[self._default_model()]
            if endpoint == default_model_info.endpoint:
                model_info = default_model_info
            else:
                model_info = self._supported_models()[UNSPECIFIED_MODEL]

        for key in model_info.required_keys:
            if key not in kwargs:
                raise errors.ArgumentNotFoundError(
                    f"The required key `{key}` is not provided."
                )
        kwargs["stream"] = stream
        return kwargs

    def _data_postprocess(self, data: QfResponse) -> QfResponse:
        """
        post process data after get request response
        """
        return data

    def _convert_endpoint(self, endpoint: str) -> str:
        """
        convert user-provided endpoint to real endpoint
        """
        raise NotImplementedError

    def models(self) -> Set[str]:
        """
        get all supported model names
        """
        models = set(self._supported_models().keys())
        models.remove(UNSPECIFIED_MODEL)
        return models

    def access_token(self) -> str:
        """
        get access token
        """
        return self._client._auth.access_token()
