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
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Set, Optional, Union, List
from qianfan.errors import InvalidArgumentError
from collections.abc import Mapping

ParamsType = Dict[str, str]
HeadersType = Dict[str, str]
JsonBody = Dict[str, Any]


def default_field(obj):
    """
    return the default field of dataclasses
    """
    return field(default_factory=lambda: copy.copy(obj))


@dataclass
class RetryConfig:
    """
    The retry config used in SDK
    """

    retry_count: int = 1
    timeout: float = 10
    backoff_factor: float = 0


@dataclass
class QfRequest:
    """
    Request object used in SDK
    """

    method: str
    url: str
    query: ParamsType = default_field({})
    headers: HeadersType = default_field({})
    json_body: JsonBody = default_field({})
    retry_config: RetryConfig = default_field(RetryConfig())

    def requests_args(self) -> Dict[str, Any]:
        """
        convert self to args of requests.request() or aiohttp.requests()
        """
        return {
            "method": self.method,
            "url": self.url,
            "params": self.query,
            "headers": self.headers,
            "json": self.json_body,
        }


@dataclass
class QfResponse(Mapping):
    """
    Response from Qianfan API
    """

    code: int
    headers: Dict[str, str] = default_field({})
    body: JsonBody = default_field({})
    image: Optional[bytes] = None

    def __getitem__(self, item):
        """
        get item by operator[]
        if the `item` is not the member of response, the `item` will be the key of `body`
        """
        try:
            return getattr(self, item)
        except AttributeError:
            pass
        if item in self.body:
            return self.body[item]
        raise KeyError(item)

    def __len__(self):
        """
        get len of response body
        """
        return len(self.body)

    def __iter__(self):
        """
        iterate over response body
        """
        return iter(self.body)


@dataclass
class QfLLMInfo:
    """
    LLM info in SDK
    """

    endpoint: str
    required_keys: Set[str] = default_field(set())
    optional_keys: Set[str] = default_field(set())


class QfRole(Enum):
    """
    Role type supported in Qianfan
    """

    User = "user"
    Assistant = "assistant"


class QfMessages:
    """
    Message list of Chat model
    """

    @dataclass
    class Message:
        """
        Internal class to express message
        """

        role: Union[QfRole, str] = QfRole.User
        content: str = default_field("")

        def _to_dict(self):
            """
            convert message to a dict
            """
            return {
                "role": self.role.value,
                "content": self.content,
            }

    def __init__(self):
        """
        Init QfMessages
        """
        self._msg_list: List[QfMessages.Message] = []

    def append(
        self, message: Union[str, QfResponse], role: Union[str, QfRole] = QfRole.User
    ):
        """
        append message to message_list
        message could be str or QfResponse
        if the type of `message` is QfResponse, the role can only be QfRole.Assistant
        """
        if isinstance(message, str):
            self._msg_list.append(QfMessages.Message(role=role, content=message))
        elif isinstance(message, QfResponse):
            try:
                msg = QfMessages.Message(
                    role=QfRole.Assistant, content=message.body["result"]
                )
                self._msg_list.append(msg)
            except:
                raise InvalidArgumentError("response not found in QfResponse")
        else:
            raise InvalidArgumentError(
                "Unsupported message type, only `str` and `QfResponse` are supported"
            )

    def _to_list(self):
        """
        convert messages to list
        """
        return [msg._to_dict() for msg in self._msg_list]
