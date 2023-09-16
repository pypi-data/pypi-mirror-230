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

import os
from typing import Dict, Optional, Union
from distutils.util import strtobool
from qianfan.utils.logging import log_warn


def _get_value_from_dict_or_var_or_env(
    dictionary: Dict, key: str, value: Optional[str], env_key: str
) -> Optional[str]:
    """
    Attempt to retrieve a value from the `dictionary` using the `key`
    if the `key` is not found, try to obtain a value from the environment variable using `env_key`
    if still not found, return None

    Args:
        dictionary (Dict): the dict to search
        key (str): the key of the value in dictionary
        env_key (str): the name of the environment variable

    Returns:
        the value of key, or None if not found
    """
    if key in dictionary:
        return dictionary[key]
    if value is not None:
        return value
    env_value = os.environ.get(env_key)
    return env_value


def _set_val_if_key_exists(src: dict, dst: dict, key: str) -> None:
    """
    if `key` is in `src` dict, set the value of `key` in dst with src[key]

    Args:
        src (Dict): the source dict
        dst (Dict): the destination dict
        key (str): the key to be found in src dict

    Returns:
        None
    """
    if key in src:
        dst[key] = src[key]


def _get_from_env_or_default(
    env_name: str, default_value: Union[str, bool]
) -> Union[str, bool]:
    """
    Get value from environment variable or return default value

    Args:
        env_name (str): the name of the environment variable
        default_value: the default value if the env var does not exist

    Return:
        str, the value of the environment variable or default_value
    """
    env_value = os.environ.get(env_name)
    if env_value is None:
        return default_value
    if isinstance(default_value, bool):
        try:
            env_value = strtobool(env_value)
        except ValueError:
            log_warn(
                f"Got unexpected bool value `{env_value}` of environment variable `{env_name}`,"
                "default value will be used."
            )
            return default_value
    return env_value
