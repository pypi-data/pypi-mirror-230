"""HubSpot client module."""

import aiohttp
import asyncio
import fondat.error
import logging

from collections import deque
from collections.abc import AsyncIterator, Callable, Coroutine
from contextlib import asynccontextmanager
from contextvars import ContextVar
from fondat.codec import JSONCodec, StringCodec
from fondat.error import InternalServerError
from fondat.pagination import Cursor, Page
from fondat.stream import Stream
from json import dumps
from typing import Any, Literal, TypeVar


_logger = logging.getLogger(__name__)


_client = ContextVar("fondat.hubspot.client._client")

_str_codec = StringCodec.get(Any)

Method = Literal["GET", "PUT", "POST", "DELETE", "PATCH"]

T = TypeVar("T")


class Client:
    """
    HubSpot API client.

    Parameters:
    • session: client session to use to make HTTP requests
    • instance_url: URL to the HubSpot instance
    • authenticator: coroutine function to authenticate and return an access token
    • retries: number of times to retry server errors

    The client acts as a context manager. It is required in runtime context through the use
    of the `with` statement by HubSpot resources to make requests to the HubSpot API.

    If a client session is not supplied to the client, a new one is created for each request.
    """

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        endpoint: str = "https://api.hubapi.com",
        authenticator: Callable[[aiohttp.ClientSession], Coroutine[Any, Any, Any]],
        retries: int = 3,
    ):
        self.session = session
        self.endpoint = endpoint
        self.authenticator = authenticator
        self.retries = retries
        self.token = None
        self._reset = deque()

    @asynccontextmanager
    async def http_request(
        self,
        method: Method,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: Any = None,
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        """
        Make an HTTP request to a HubSpot API endpoint.

        Parameters:
        • method: HTTP request method
        • path: request path, relative to endpoint URL
        • headers: HTTP headers to include in request
        • params: query parameters to include in request
        • json: JSON body data to include in request

        This method is an asynchronous context manager; it keeps an HTTP connection open while
        it remains in runtime context.
        """

        if headers is None:
            headers = {}

        auth_errors = 0
        server_errors = 0

        while True:
            if not self.token:
                _logger.debug("acquiring authentication token")
                self.access_token = await self.authenticator(self.session)
            headers["Authorization"] = f"Bearer {self.access_token}"
            url = f"{self.endpoint}{path}"
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
            ) as response:
                _logger.debug("%s %s %d", method, url, response.status)
                if 200 <= response.status <= 299:
                    yield response
                    return
                elif response.status == 401 and auth_errors < 1:
                    _logger.debug("retrying authentication")
                    auth_errors += 1
                    self.token = None
                    continue
                elif 500 <= response.status <= 599 and server_errors < self.retries:
                    _logger.debug(f"retrying server error")
                    await asyncio.sleep(2**server_errors)
                    server_errors += 1
                    continue
                elif 400 <= response.status <= 599:
                    raise fondat.error.errors[response.status](await response.text())
                else:
                    raise fondat.error.InternalServerError(
                        f"unexpected response: {response.status} {await response.text()}"
                    )

    async def typed_request(
        self,
        method: Method,
        path: str,
        params: dict[str, Any] | None = None,
        request_body: Any = None,
        response_type: type[T] = None,
    ) -> T:
        """
        Make an HTTP request to a HubSpot API endpoint with a typed request and/or response
        body.

        Parameters:
        • method: HTTP request method
        • path: request path, relative to endpoint URL
        • params: query parameters to include in request
        • request_body: object to encode as JSON body
        • response_type: type to decode JSON response
        """

        if params:
            params = {k: _str_codec.encode(v) for k, v in params.items() if v is not None}

        async with self.http_request(
            method=method,
            path=path,
            params=params,
            json=JSONCodec.get(Any).encode(request_body) if request_body else None,
        ) as response:
            if response_type:
                return JSONCodec.get(response_type).decode(await response.json())

    async def paged_request(
        self,
        method: Method,
        path: str,
        item_type: T,
        params: dict[str, Any] | None = None,
        json: Any = None,
        limit: int | None = None,
        cursor: Cursor = None,
    ) -> Page[T]:
        """
        Get a paginated list of items via the HubSpot v3+ API.

        Parameters:
        • path: request path, relative to endpoint URL
        • item_type: type to decode for items in JSON response
        • params: extra parameters to include in query string
        • limit: maximum number of items to return in page
        • cursor: cursor to fetch next page

        This translates between pagination in Fondat `cursor` and HubSpot `after` in
        HubSpot v3+ APIs.
        """
        codec = JSONCodec.get(list[item_type])
        params = {
            k: _str_codec.encode(v) for k, v in (params or dict()).items() if v is not None
        }
        if limit:
            params["limit"] = str(limit)
        if cursor:
            params["after"] = cursor.decode()
        async with get_client().http_request(
            method=method, path=path, params=params, json=json
        ) as response:
            json = await response.json()
        try:
            cursor = json["paging"]["next"]["after"].encode()
        except KeyError:
            cursor = None
        return Page(items=codec.decode(json["results"]), cursor=cursor)

    def __enter__(self):
        self._reset.append(_client.set(self))
        return self

    def __exit__(self, *_):
        _client.reset(self._reset.pop())


def get_client() -> Client:
    """Return the current client in runtime context."""
    try:
        return _client.get()
    except LookupError as le:
        raise InternalServerError from le


class HTTPResponseStream(Stream):
    """
    ...

    Parameters and attributes:
    • response: HTTP response to stream
    """

    def __init__(self, response: aiohttp.ClientResponse):
        super().__init__(response.content_type, response.content_length)
        self.content = response.content.iter_any()

    async def __anext__(self) -> bytes:
        if not self.content:
            raise StopAsyncIteration
        return await self.content.__anext__()

    async def close(self) -> None:
        self.content = None
