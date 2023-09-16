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
"""utils for logging
"""
import logging


class Logger(object):
    _DEFAULT_MSG_FORMAT = "[%(levelname)s] [%(asctime)s] %(filename)s:%(lineno)d [t:%(thread)d]: %(message)s"
    _DEFAULT_DATE_FORMAT = "%m-%d %H:%M:%S"

    def __init__(
        self, name="qianfan", format=_DEFAULT_MSG_FORMAT, datefmt=_DEFAULT_DATE_FORMAT
    ) -> None:
        """
        Args:
            - name (str): name of logger, default "qianfan".
            - format (_DEFAULT_MSG_FORMAT): log message format, default `_DEFAULT_MSG_FORMAT`
            - datefmt (_DEFAULT_DATE_FORMAT): time format, default `_DEFAULT_DATE_FORMAT`

        Returns:
            None
        """
        # 创建一个loggger
        self.__name = name
        self._logger = logging.getLogger(self.__name)
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter(format, datefmt)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def info(self, message: object, *args: object, **params):
        """
        INFO level log

        Args:
            message (object): message content

        Returns:
            None

        """
        return self._logger.info(message, *args, **params)

    def debug(self, message: object, *args: object, **params):
        """
        DEBUG level log

        Args:
            message (object): message content

        Returns:
            None
        """
        self._logger.debug(message, args, params)

    def error(self, message: object, *args: object, **params):
        """
        ERROR level log

        Args:
            message (object): message content

        Returns:
            None
        """
        self._logger.error(message, args, params)

    def warn(self, message: object, *args: object, **params):
        """
        WARN level log

        Args:
            message (object): message content

        Returns:
            None

        """
        self._logger.warn(message, args, params)


logger = Logger()

log_info = logger.info
log_debug = logger.debug
log_error = logger.error
log_warn = logger.warn
