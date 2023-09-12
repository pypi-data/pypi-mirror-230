import asyncio
import json
import platform
import warnings
from contextlib import asynccontextmanager
from typing import Tuple, Union, Iterator, Optional, Dict, AsyncGenerator, AsyncIterator
from urllib.parse import urlencode, urlsplit, urlunsplit
import threading

import aiohttp
import requests
from json import JSONDecodeError

import sensenova
from sensenova import util, error, version
from sensenova.sensenova_response import SensenovaResponse

MAX_CONNECTION_RETRIES = 2
_thread_context = threading.local()


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlsplit(url)

    if base_query:
        query = "%s%s" % (base_query, query)

    return urlunsplit((scheme, netloc, path, query, fragment))


def _make_session() -> requests.Session:
    if sensenova.requestssession:
        if isinstance(sensenova.requestssession, requests.Session):
            return sensenova.requestssession
        return sensenova.requestssession()
    if not sensenova.verify_ssl_certs:
        warnings.warn("verify_ssl_certs is ignored; sensenova always verifies.")
    s = requests.Session()
    s.mount(
        "https://",
        requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES)
    )
    return s


def parse_stream_helper(line: str) -> Optional[str]:
    # TODO: Adapt to chat
    if line:
        if line.strip() == b"data:[DONE]":
            return None

        if line.startswith(b"data:"):
            line = line[len(b"data:"):]
            return line.decode("utf-8")
        else:
            return None
    return None


def parse_stream(rbody: Iterator[bytes]) -> Iterator[str]:
    for line in rbody:
        _line = parse_stream_helper(line)
        if _line is not None:
            yield _line


async def parse_stream_async(rbody: aiohttp.StreamReader) -> str:
    async for line in rbody:
        _line = parse_stream_helper(line)
        if _line is not None:
            yield _line


class APIRequestor:
    def __init__(self, access_key_id=None,
                 secret_access_key=None, api_base=None, api_version=None):
        self.access_key_id = access_key_id or util.default_access_key_id()
        self.secret_access_key = secret_access_key or util.default_secret_access_key()
        self.api_base = api_base or sensenova.api_base

    @classmethod
    def format_app_info(cls, info):
        s = info["name"]
        if info["version"]:
            s += "/%s" % (info["version"],)
        if info["url"]:
            s += " (%s)" % (info["url"],)
        return s

    def request(self, method: str, url: str, params=None, headers=None, files=None, stream: bool = False) -> Tuple[
        Union[SensenovaResponse, Iterator[SensenovaResponse]], bool, str, str]:
        result = self.request_raw(
            method.lower(),
            url,
            params=params,
            supplied_headers=headers,
            files=files,
            stream=stream,
        )
        resp, got_stream = self._interpret_response(result, stream)
        return resp, got_stream, self.access_key_id, self.secret_access_key

    async def arequest(
        self,
        method: str,
        url: str,
        params=None,
        headers=None,
        files=None,
        stream: bool = False
    ) -> Tuple[Union[SensenovaResponse, AsyncGenerator[SensenovaResponse, None]], bool, str, str]:
        ctx = aiohttp_session()
        session = await ctx.__aenter__()

        try:
            result = await self.arequest_raw(
                method.lower(),
                url,
                session,
                params=params,
                supplied_headers=headers,
                files=files,
            )
            resp, got_stream = await self._interpret_async_response(result, stream)
        except Exception:
            await ctx.__aexit__(None, None, None)
            raise
        if got_stream:
            async def wrap_resp():
                assert isinstance(resp, AsyncGenerator)
                try:
                    async for r in resp:
                        yield r
                finally:
                    await ctx.__aexit__(None, None, None)

            return wrap_resp(), got_stream, self.access_key_id, self.secret_access_key
        else:
            await ctx.__aexit__(None, None, None)
            return resp, got_stream, self.access_key_id, self.secret_access_key

    def _interpret_response_line(
        self, rbody: str, rcode: int, rheaders, stream: bool
    ) -> SensenovaResponse:
        if rcode == 204:
            return SensenovaResponse(None, rheaders)

        if rcode == 503:
            raise error.ServiceUnavailableError(
                "The server is overloaded or not ready yet.",
                rbody,
                rcode,
                headers=rheaders,
            )
        try:
            if 'text/plain' in rheaders.get('Content-Type', ''):
                data = rbody
            else:
                data = json.loads(rbody)
        except (JSONDecodeError, UnicodeDecodeError) as e:
            try:
                if self.api_base == 'https://aoss' and rbody == '':
                    data = {
                        "info": "Created"
                    }
                else:
                    data = eval(rbody)

            except Exception as exp:
                raise error.APIError(
                    f"HTTP code {rcode} from API ({rbody})", rbody, rcode, headers=rheaders
                ) from e
        resp = SensenovaResponse(data, rheaders)
        stream_error = stream and "error" in resp.data
        if stream_error or not 200 <= rcode < 300:
            raise self.handle_error_response(
                rbody, rcode, resp.data, rheaders, stream_error=stream_error
            )
        return resp

    def _interpret_response(self, result: requests.Response, stream: bool) -> Tuple[
        Union[SensenovaResponse, Iterator[SensenovaResponse]], bool]:
        if stream and "text/event-stream" in result.headers.get("Content-Type", ""):
            return (
                self._interpret_response_line(
                    line, result.status_code, result.headers, stream=True
                )
                for line in parse_stream(result.iter_lines())
            ), True
        else:
            return (
                self._interpret_response_line(
                    result.content.decode('utf-8'),
                    result.status_code,
                    result.headers,
                    stream=False
                ),
                False
            )

    def request_raw(self, method, url, *, params=None, supplied_headers: Optional[Dict[str, str]] = None, files=None,
                    stream: bool = False) -> requests.Response:
        abs_url, headers, data = self._prepare_request_raw(
            url, supplied_headers, method, params, files
        )

        if not hasattr(_thread_context, "session"):
            _thread_context.session = _make_session()
        try:
            result = _thread_context.session.request(
                method,
                abs_url,
                headers=headers,
                data=data,
                files=files,
                stream=stream,
                verify=sensenova.verify_ssl_certs
            )
        except requests.exceptions.RequestException as e:
            raise error.APIConnectionError(
                "Error communicating with Sensenova: {}".format(e)
            ) from e
        util.log_debug(
            "Sensenova API response",
            path=abs_url,
            response_code=result.status_code,
        )

        if sensenova.log == 'debug':
            util.log_debug(
                "API response body", body=result.content, headers=result.headers
            )
        return result

    async def arequest_raw(
        self,
        method,
        url,
        session,
        *,
        params=None,
        supplied_headers: Optional[Dict[str, str]] = None,
        files=None,
        allow_redirects=True,
    ) -> aiohttp.ClientResponse:
        abs_url, headers, data = self._prepare_request_raw(
            url, supplied_headers, method, params, files
        )

        if files:
            data, content_type = requests.models.RequestEncodingMixin._encode_files(
                files, data
            )
            headers["Content-Type"] = content_type

        request_kwargs = {
            "method": method,
            "url": abs_url,
            "headers": headers,
            "data": data,
            "allow_redirects": allow_redirects,
        }

        try:
            result = await session.request(**request_kwargs)
            util.log_info(
                "Sensenova API response",
                path=abs_url,
                response_code=result.status,
            )
            return result
        except aiohttp.ClientError as e:
            raise error.APIConnectionError("Error communicating with Sensenova") from e

    def _prepare_request_raw(self, url, supplied_headers, method, params, files) -> Tuple[
        str, Dict[str, str], Optional[bytes]]:
        abs_url = "%s%s" % (self.api_base, url)
        headers = self._validate_headers(supplied_headers)

        data = None
        if method == "get" or method == "delete":
            if params:
                encoded_params = urlencode(
                    [(k, v) for k, v in params.items() if v is not None]
                )
                abs_url = _build_api_url(abs_url, encoded_params)
        elif method in {"post", "put"}:
            if self.api_base == 'https://aoss':
                data = params
                headers = {"Content-Type": "application/octet-stream"}
            else:
                if params and files:
                    data = params
                if params and not files:
                    data = json.dumps(params).encode()
                    headers["Content-Type"] = "application/json"
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r. This may indicate a bug in the "
                "Sensenova bindings. Please contact us" % method
            )

        headers = self.request_headers(method, headers)

        util.log_debug("Request to Sensenova API", method=method, path=abs_url)
        util.log_debug("Post details", data=data)

        return abs_url, headers, data

    def _validate_headers(self, supplied_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if supplied_headers is None:
            return headers

        if not isinstance(supplied_headers, dict):
            raise TypeError("Headers must be a dictionary")

        for k, v in supplied_headers.items():
            if not isinstance(k, str):
                raise TypeError("Header keys must be strings")
            if not isinstance(v, str):
                raise TypeError("Header values must be strings")
            headers[k] = v

        return headers

    def request_headers(self, method: str, extra) -> Dict[str, str]:
        user_agent = "Sensenova/v1 PythonBindings/%s" % (version.VERSION,)
        if sensenova.app_info:
            user_agent += " " + self.format_app_info(sensenova.app_info)

        uname_without_node = " ".join(
            v for k, v in platform.uname()._asdict().items() if k != "node"
        )

        ua = {
            "bindings_version": version.VERSION,
            "httplib": "requests",
            "lang": "python",
            "lang_version": platform.python_version(),
            "platform": platform.platform(),
            "publisher": "sensenova",
            "uname": uname_without_node,
        }

        if sensenova.app_info:
            ua['application'] = sensenova.app_info

        if self.api_base != 'https://aoss':
            headers = {
                "X-Sensenova-Client-User-Agent": json.dumps(ua),
                "User-Agent": user_agent,
            }
            headers.update(util.ak_sk_to_header(self.access_key_id, self.secret_access_key))
        else:
            headers = {}
        if sensenova.debug:
            headers["Sensenova-Debug"] = "true"
        headers.update(extra)

        return headers

    @classmethod
    def handle_error_response(cls, rbody, rcode, resp, rheaders, stream_error=False):
        try:
            error_data = resp["error"]
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                rbody,
                rcode,
                resp,
            )

        util.log_info(
            "Sensenova API error received",
            error_code=error_data.get("code"),
            error_message=error_data.get("message"),
            stream_error=stream_error,
        )

        if rcode in [400, 404, 415]:
            return error.InvalidRequestError(
                error_data.get("message"),
                None,
                error_data.get("code"),
                rbody,
                rcode,
                resp,
                rheaders,
            )
        elif rcode == 429:
            return error.RateLimitError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 401:
            return error.AuthenticationError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 403:
            return error.PermissionError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 409:
            return error.TryAgain(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif stream_error:
            parts = [error_data.get("message"), "(Error occurred while streaming.)"]
            message = " ".join([p for p in parts if p is not None])
            return error.APIError(message, rbody, rcode, resp, rheaders)
        else:
            return error.APIError(
                f"{error_data.get('message')} {rbody} {rcode} {resp} {rheaders}",
                rbody,
                rcode,
                resp,
                rheaders,
            )

    async def _interpret_async_response(self, result: aiohttp.ClientResponse, stream: bool) -> Tuple[Union[
        SensenovaResponse, AsyncGenerator[SensenovaResponse, None]], bool]:
        if stream and "text/event-stream" in result.headers.get("Content-Type", ""):
            return (
                self._interpret_response_line(
                    line, result.status, result.headers, stream=True
                )
                async for line in parse_stream_async(result.content)
            ), True
        else:
            try:
                await result.read()
            except aiohttp.ClientError as e:
                util.log_warn(e, body=result.content)
            return (
                self._interpret_response_line(
                    (await result.read()).decode("utf-8"),
                    result.status,
                    result.headers,
                    stream=False,
                ),
                False,
            )


@asynccontextmanager
async def aiohttp_session() -> AsyncIterator[aiohttp.ClientSession]:
    user_set_session = sensenova.aiosession.get()
    if user_set_session:
        yield user_set_session
    else:
        async with aiohttp.ClientSession() as session:
            yield session
