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

"""the collection of errors for this library
"""


class QianfanError(Exception):
    """Base exception class for the qianfan sdk."""

    pass


class NotImplmentError(QianfanError):
    """Exception that's raised when code not implemented."""

    pass


class QianfanAPIError(Exception):
    """Base exception clas for the qianfan api error"""

    pass


class InvalidArgumentError(QianfanError):
    """Exception when the argument is invalid"""

    pass


class ArgumentNotFoundError(QianfanError):
    """Exception when the argument is not found"""

    pass
