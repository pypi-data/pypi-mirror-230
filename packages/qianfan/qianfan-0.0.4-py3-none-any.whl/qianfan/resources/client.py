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

import threading
import json
import requests
import aiohttp
import time
import asyncio

from typing import Dict, Any

import qianfan.errors as errors
from qianfan.consts import APIErrorCode
from qianfan.resources.auth import Auth
from qianfan.config import GLOBAL_CONFIG
from qianfan.resources.http_client import HTTPClient
from qianfan.resources.typing import RetryConfig, QfResponse, QfRequest
from qianfan.utils.logging import log_error, log_info, log_warn


STREAM_RESPONSE_PREFIX = "data: "


class QfClient(object):
    """
    object to manage Qianfan API requests
    """

    def __init__(self, **kwargs) -> None:
        """
        `ak`, `sk` and `access_token` can be provided in kwargs.
        """
        self._client = HTTPClient()
        self._auth = Auth(**kwargs)
        self._lock = threading.Lock()

    def _request(self, request: QfRequest, data_postprocess=lambda x: x) -> QfResponse:
        """
        simple sync request
        """
        response = self._client.request(request)
        body = response.json()
        return data_postprocess(self._parse_response(body, response))

    def _request_stream(self, request: QfRequest, data_postprocess=lambda x: x):
        """
        stream sync request
        """
        responses = self._client.request_stream(request)
        for body, resp in responses:
            body_str = body.decode("utf-8")
            if body_str == "":
                continue
            if not body_str.startswith(STREAM_RESPONSE_PREFIX):
                try:
                    # the response might be error message in json format
                    body = json.loads(body_str)
                    self._check_error(body)
                except json.JSONDecodeError:
                    # the response is not json format, ignore and raise InternalError
                    pass

                raise errors.InternalError(
                    f"got unexpected stream response from server: {body_str}"
                )
            body_str = body_str[len(STREAM_RESPONSE_PREFIX) :]
            body = json.loads(body_str)
            parsed = self._parse_response(body, resp)
            yield data_postprocess(parsed)

    async def _async_request(
        self, request: QfRequest, data_postprocess=lambda x: x
    ) -> QfResponse:
        """
        async request
        """
        response, session = await self._client.arequest(request)
        async with session:
            async with response:
                body = await response.json()
                return data_postprocess(self._parse_async_response(body, response))

    async def _async_request_stream(
        self, request: QfRequest, data_postprocess=lambda x: x
    ):
        """
        async stream request
        """
        responses = self._client.arequest_stream(request)
        async for body, resp in responses:
            body_str = body.decode("utf-8")
            if body_str.strip() == "":
                continue
            if not body_str.startswith(STREAM_RESPONSE_PREFIX):
                try:
                    # the response might be error message in json format
                    body = json.loads(body_str)
                    self._check_error(body)
                except json.JSONDecodeError:
                    # the response is not json format, ignore and raise InternalError
                    pass
                raise errors.InternalError(
                    f"got unexpected stream response from server: {body_str}"
                )
            body_str = body_str[len(STREAM_RESPONSE_PREFIX) :]
            body = json.loads(body_str)
            parsed = self._parse_async_response(body, resp)
            yield data_postprocess(parsed)

    def llm(
        self,
        endpoint,
        header={},
        query={},
        body={},
        stream=False,
        data_postprocess=lambda x: x,
        retry_config=RetryConfig(),
    ) -> QfResponse:
        """
        llm related api request
        """
        log_info(f"requesting llm api endpoint: {endpoint}")

        def _helper():
            req = self._convert_to_llm_request(
                endpoint,
                header=header,
                query=query,
                body=body,
                retry_config=retry_config,
            )
            if stream:
                return self._request_stream(req, data_postprocess=data_postprocess)
            return self._request(req, data_postprocess=data_postprocess)

        return self._with_retry(retry_config, _helper)

    async def async_llm(
        self,
        endpoint,
        header={},
        query={},
        body={},
        stream=False,
        data_postprocess=lambda x: x,
        retry_config=RetryConfig(),
    ) -> QfResponse:
        """
        llm related api request
        """
        log_info(f"async requesting llm api endpoint: {endpoint}")

        async def _helper():
            req = self._convert_to_llm_request(
                endpoint,
                header=header,
                query=query,
                body=body,
                retry_config=retry_config,
            )
            if stream:
                return self._async_request_stream(
                    req, data_postprocess=data_postprocess
                )
            return await self._async_request(req, data_postprocess=data_postprocess)

        return await self._async_with_retry(retry_config, _helper)

    def _convert_to_llm_request(
        self, endpoint, header={}, query={}, body={}, retry_config=RetryConfig()
    ):
        """
        convert args to llm request
        1. convert endpoint to api url
        2. add access_token
        """
        req = QfRequest(method="POST", url=self._llm_api_url(endpoint))
        req.headers = header
        access_token = self._auth.access_token()
        if access_token == "":
            raise errors.AccessTokenExpiredError
        req.query = {"access_token": access_token, **query}
        req.json_body = body
        req.retry_config = retry_config
        return req

    def _parse_response(
        self, body: Dict[str, Any], resp: requests.Response
    ) -> QfResponse:
        """
        parse response to QfResponse
        """
        self._check_error(body)
        qf_response = QfResponse(
            code=resp.status_code, headers=dict(resp.headers), body=body
        )
        return qf_response

    def _parse_async_response(
        self, body: Dict[str, Any], resp: aiohttp.ClientResponse
    ) -> QfResponse:
        """
        parse async response to QfResponse
        """
        self._check_error(body)

        qf_response = QfResponse(
            code=resp.status, headers=dict(resp.headers), body=body
        )
        return qf_response

    def _check_error(self, body: Dict[str, Any]):
        """
        check whether "error_code" is in response
        if got error, APIError exception will be raised
        """
        if "error_code" in body:
            error_code = body["error_code"]
            err_msg = body.get(
                "error_msg",
                f"no error message in return body, error code: {error_code}",
            )
            log_error(
                f"api request failed with error code: {error_code}, err msg: {err_msg}"
            )
            if error_code in [
                APIErrorCode.APITokenExpired,
                APIErrorCode.APITokenInvalid,
            ]:
                raise errors.AccessTokenExpiredError
            raise errors.APIError(error_code, err_msg)

    def _llm_api_url(self, endpoint: str) -> str:
        """
        convert endpoint to llm api url
        """
        return "{}{}{}".format(
            GLOBAL_CONFIG.BASE_URL,
            GLOBAL_CONFIG.MODEL_API_PREFIX,
            endpoint,
        )

    def _with_retry(self, config: RetryConfig, func, *args):
        """
        retry wrapper
        """
        i = 0
        token_refreshed = False
        while i < config.retry_count:
            try:
                return func(*args)
            except errors.APIError as e:
                if e.error_code in {APIErrorCode.ServerHighLoad}:
                    log_warn(
                        f"got error code {e.error_code} from server, retrying... count: {i}"
                    )
                    continue
            except errors.AccessTokenExpiredError:
                self._auth.refresh_access_token()
                if token_refreshed:
                    # only refresh token once, if token is still expired, raise exception
                    raise
                # try again
                i -= 1
                token_refreshed = True
            except requests.RequestException as e:
                log_error(f"request exception: {e}, retrying... count: {i}")
                continue

            time.sleep(config.backoff_factor * (2**i))
            i += 1

    async def _async_with_retry(self, config: RetryConfig, func, *args):
        """
        async retry wrapper
        """
        i = 0
        token_refreshed = False
        while i < config.retry_count:
            try:
                return await func(*args)
            except errors.APIError as e:
                if e.error_code in {APIErrorCode.ServerHighLoad}:
                    log_warn(
                        f"got error code {e.error_code} from server, retrying... count: {i}"
                    )
                    continue
            except errors.AccessTokenExpiredError:
                self._auth.refresh_access_token()
                if token_refreshed:
                    # only refresh token once, if token is still expired, raise exception
                    raise
                # try again
                i -= 1
                token_refreshed = True
            except aiohttp.ClientError as e:
                log_error(f"async request exception: {e}, retrying... count: {i}")
                continue
            await asyncio.sleep(config.backoff_factor * (2**i))
            i += 1
