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

from typing import Any, Optional

import qianfan.errors as errors
from qianfan.resources.llm.base import BaseResource, UNSPECIFIED_MODEL
from qianfan.resources.typing import JsonBody
from qianfan.consts import DefaultLLMModel
from qianfan.resources.typing import QfLLMInfo


class Embedding(BaseResource):
    """Get the embedding of the given texts."""

    def _supported_models(self):
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
            "Embedding-V1": QfLLMInfo(
                endpoint="/embeddings/embedding-v1",
                required_keys={"input"},
                optional_keys={"user_id"},
            ),
            "bge-large-en": QfLLMInfo(
                endpoint="/embeddings/bge_large_zh",
                required_keys={"input"},
                optional_keys={"user_id"},
            ),
            "bge-large-zh": QfLLMInfo(
                endpoint="/embeddings/bge_large_en",
                required_keys={"input"},
                optional_keys={"user_id"},
            ),
            UNSPECIFIED_MODEL: QfLLMInfo(
                endpoint="", required_keys={"input"}, optional_keys={}
            ),
        }

    def _default_model(self):
        """
        default model of Embedding `Embedding-V1`

        Args:
            None

        Returns:
           "Embedding-V1"

        """
        return DefaultLLMModel.Embedding

    def _generate_body(
        self, model: Optional[str], endpoint: str, stream: bool, **kwargs: Any
    ) -> JsonBody:
        """
        need to check whether stream is set in Embedding
        """
        if stream == True:
            raise errors.InvalidArgumentError("Stream is not supported for embedding")
        if "texts" not in kwargs:
            raise errors.ArgumentNotFoundError(f"input not found in kwargs")
        kwargs["input"] = kwargs["texts"]
        del kwargs["texts"]
        return super()._generate_body(model, endpoint, stream, **kwargs)

    def _convert_endpoint(self, endpoint: str) -> str:
        """
        convert endpoint to Embedding API endpoint
        """
        return f"/embeddings/{endpoint}"
