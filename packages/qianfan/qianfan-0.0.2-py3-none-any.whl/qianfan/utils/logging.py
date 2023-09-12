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
            - name (str): 日志器的名字，默认为'qianfan'。
            - format (_DEFAULT_MSG_FORMAT): 日志消息格式化字符串，默认为_DEFAULT_MSG_FORMAT。
            - datefmt (_DEFAULT_DATE_FORMAT): 时间格式化字符串，默认为_DEFAULT_DATE_FORMAT。

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
        记录信息日志

        Args:
            message (object): 消息内容
            *args (tuple[object]): 可变参数列表
            **params (dict[str, object]): 参数字典

        Returns:
            None

        """
        return self._logger.info(message, *args, **params)

    def debug(self, message: object, *args: object, **params):
        """
        调试日志方法

        Args:
            message (object): 需要输出的消息对象
            *args (object): 可变参数列表
            **params (dict): 参数字典

        Returns:
            None
        """
        self._logger.debug(message, args, params)

    def error(self, message: object, *args: object, **params):
        """
        记录错误日志。

        Args:
            message (object): 日志消息，可以是字符串或可打印对象的类型。
            *args (object): 可变参数列表，用于格式化日志消息中的占位符。
            **params (dict): 以键值对的形式指定额外的参数。

        Returns:
            None
        """
        self._logger.error(message, args, params)

    def warn(self, message: object, *args: object, **params):
        """
        记录警告信息

        Args:
            message (object): 警告信息的对象
            *args (object): 可变参数，包含附加的参数
            **params (dict): 参数字典

        Returns:
            None

        """
        self._logger.warn(message, args, params)


logger = Logger()

log_info = logger.info
log_debug = logger.debug
log_error = logger.error
log_warn = logger.warn
