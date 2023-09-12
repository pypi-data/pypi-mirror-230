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

import erniebot
from erniebot.types import FilesType, HeadersType, ParamsType
from erniebot.response import EBResponse
import qianfan.errors as errors
from qianfan.resources.base import BaseResource
from typing import Any, Dict, List, Tuple, Union, Optional, Iterator, AsyncIterator
from qianfan.utils import log_info

QIANFAN_DEFAULT_EMBEDDING_MODEL = "Embedding-V1"


class Embedding(BaseResource):
    """Get the embedding of the given texts."""

    def __init__(self, **kwargs) -> None:
        """
        Init for the Qianfan embedding object.

        Args:
            None

        """
        super().__init__(**kwargs)

    def do(self, texts: List[str], **kwargs) -> Union[EBResponse, Iterator[EBResponse]]:
        """
        Get the embedding of the input texts

        Args:
            texts (List[str]): list of the input texts

        Returns:
            List[EBResponse]: list of embedding vectors of each text

        """
        kwargs["endpoint"] = self._get_endpoint_from_dict(**kwargs)
        return QfEmbeddingAPIResource().create(input=texts, **kwargs)

    async def ado(
        self, texts: List[str], **kwargs
    ) -> Union[EBResponse, AsyncIterator[EBResponse]]:
        """
        aio get the embedding of the input texts

        Args:
            texts (List[str]): the list of texts。

            kwargs:

        Returns:
            List[EBResponse]: list of embedding vectors of each text

        """
        kwargs["endpoint"] = self._get_endpoint_from_dict(**kwargs)
        return await QfEmbeddingAPIResource().acreate(input=texts, **kwargs)

    def _supported_model_endpoint(self):
        """
        preset model list of Embedding
        support model:
         - Embedding-V1
         - bge-large-en
         - bge-large-zh

        Args:
            None

        Returns:
            a dict which key is preset model and value is the endpoint

        """
        return {
            "Embedding-V1": "embedding-v1",
            "bge-large-en": "bge_large_en",
            "bge-large-zh": "bge_large_zh",
        }

    def _default_model(self):
        """
        default model of Embedding `Embedding-V1`

        Args:
            None

        Returns:
           "Embedding-V1"

        """
        return QIANFAN_DEFAULT_EMBEDDING_MODEL


class QfEmbeddingAPIResource(erniebot.Embedding):
    """
    QianFan Embedding Resource

    providing access to QianFan "embedding" API.

    """

    # the prefix of the endpoint in "embedding" qianfan url
    _URL_PREFIX = "embeddings"

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
            ArgumentNotFoundError: thrown when endpoint or input is not found
        """
        REQUIRED_KEYS = {"endpoint", "input"}
        for key in REQUIRED_KEYS:
            if key not in kwargs:
                raise errors.ArgumentNotFoundError(f"Missing required key: {key}")

        input = kwargs["input"]

        url = f"/{self._URL_PREFIX}/{kwargs['endpoint']}"
        log_info("requesting url: %s" % url)
        params = {"input": input}
        if "user_id" in kwargs:
            params["user_id"] = kwargs["user_id"]

        headers = kwargs.get("headers", None)
        files = None
        stream = kwargs.get("stream", False)
        request_timeout = kwargs.get("request_timeout", None)

        return url, params, headers, files, stream, request_timeout
