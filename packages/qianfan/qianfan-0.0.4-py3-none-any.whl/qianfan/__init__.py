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

"""qianfan library
Library that wraps the qianfan API.
"""

from qianfan.resources import ChatCompletion, Embedding, Completion, Plugin
from qianfan.resources.typing import QfResponse, QfRole, QfMessages
from qianfan.version import VERSION
from qianfan.config import GLOBAL_CONFIG, AK, SK, AccessToken

Role = QfRole
Messages = QfMessages
Response = QfResponse

__all__ = ["ChatCompletion", "Embedding", "Completion", "Plugin"]
__version__ = VERSION
