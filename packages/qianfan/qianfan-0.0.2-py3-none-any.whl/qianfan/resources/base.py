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
import erniebot
import os
import qianfan.errors as errors
from erniebot.response import EBResponse
from qianfan.utils import _get_value_from_dict_or_env


class BaseResource(object):
    """
    base class of Qianfan object
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        init resource

        """
        ak = _get_value_from_dict_or_env(kwargs, "ak", "QIANFAN_AK")
        sk = _get_value_from_dict_or_env(kwargs, "sk", "QIANFAN_SK")
        if ak is None or sk is None:
            raise ValueError("both ak and sk must be provided")
        erniebot.ak = ak
        erniebot.sk = sk
        if "endpoint" in kwargs:
            self._endpoint = kwargs["endpoint"]
        else:
            model = kwargs.get("model", self._default_model())
            self._endpoint = self._get_endpoint(model)

    def do(self, **kwargs) -> Union[EBResponse, Iterator[EBResponse]]:
        """
        qianfan resource basic do

        Args:
            **kwargs (dict): kv dict data。

        """
        raise NotImplementedError

    async def ado(self, **kwargs) -> Union[EBResponse, AsyncIterator[EBResponse]]:
        """
        qianfan aio resource basic do

        Args:
            **kwargs: kv dict data

        Returns:
            None

        """
        raise NotImplementedError

    def _supported_model_endpoint(self) -> Dict[str, str]:
        """
        preset model list

        Args:
            None

        Returns:
            a dict which key is preset model and value is the endpoint

        """
        raise NotImplementedError

    def _default_model(self):
        """
        default model

        Args:
            None

        Return:
            a str which is the default model name
        """
        raise NotImplementedError

    def _get_endpoint(self, model: str) -> str:
        """
        get the endpoint of the given `model`

        Args:
            model (str): the name of the model, must be defined in _SUPPORTED_MODEL_ENDPOINTS

        Returns:
            str: the endpoint of the input `model`

        Raises:
            QianfanError: if the input is not in _SUPPORTED_MODEL_ENDPOINTS
        """
        if model not in self._supported_model_endpoint():
            raise errors.InvalidArgumentError(f"Unsupport model {model}")
        return self._supported_model_endpoint()[model]

    def _get_endpoint_from_dict(self, **kwargs) -> str:
        """
        extract the endpoint of the model in kwargs, or use the endpoint defined in __init__

        Args:
            **kwargs (dict): any dict

        Returns:
            str: the endpoint of the model in kwargs

        """
        if "endpoint" in kwargs:
            return kwargs["endpoint"]
        if "model" in kwargs:
            return self._get_endpoint(kwargs["model"])
        return self._endpoint
