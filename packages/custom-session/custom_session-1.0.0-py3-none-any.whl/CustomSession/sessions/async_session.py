from __future__ import annotations
from dataclasses import dataclass, field

import httpx
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    AuthTypes,
    TimeoutTypes,
    RequestExtensions,
    RequestData,
    RequestContent,
    RequestFiles,
)
from httpx._exceptions import TimeoutException, ReadTimeout
import ua_generator
import asyncio
from httpx import AsyncClient
from typing import *
from ua_generator.useragent import UserAgent
from httpx import Response as httpxResponse

try:
    from models import SessionMetaData
    from exceptions import RetriesExceeded
except ImportError:
    from ..models import SessionMetaData
    from ..exceptions import RetriesExceeded


@dataclass
class AsyncSession(AsyncClient):
    """
    An asynchronous HTTP client inherited from httpx.AsyncClient that maintains unique a user-agent, metadata, and proxy.

    Usage:

    ```
    async with AsyncSession() as client:
        response = await client.get('https://example.org')
    ```

    **Parameters:**
    * **proxy** - *(optional)* HTTP/s proxy to use when sending
    requests.
    * **ignore_exceptions** - *(optional)* Tuple of Exceptions to be ignored when sending requests
    * **auth** - *(optional)* An authentication class to use when sending
    requests.
    * **meta_data** - *(optional)* A dict to use when persistent miscellaneous session data is required
    """

    proxy: str | None = field(default=None)
    ignore_exceptions: Tuple[Type[Exception]] = field(repr=False, default_factory=tuple)
    auth: AuthTypes | None = field(default=None)
    user_agent: UserAgent = field(
        init=False, repr=False, default=ua_generator.generate(device="desktop")
    )
    meta_data: SessionMetaData | dict = field(default_factory=SessionMetaData)

    async def __aenter__(self) -> AsyncSession:
        await super().__aenter__()
        return self

    async def __aexit__(self, *exc_info):
        await super().__aexit__(*exc_info)

    def __post_init__(self):
        if self.proxy is None:
            proxies = None
        else:
            proxies = {
                "http://": f"http://{self.proxy}",
                "https://": f"http://{self.proxy}",
            }
        super().__init__(auth=self.auth, proxies=proxies)
        self.headers["user-agent"] = self.user_agent.text
        if not isinstance(self.meta_data, SessionMetaData):
            self.meta_data = SessionMetaData(self.meta_data)

    async def get(
        self,
        url: str,
        retries: int = 3,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP GET request with optional retries.

        :param url: The URL to send the GET request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().get(
                    url,
                    params=params,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                    headers=headers,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def post(
        self,
        url: str,
        retries: int = 3,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
        *args,
        **kwargs,
    ) -> httpxResponse:
        """
        Send an HTTP POST request with optional retries.

        :param url: The URL to send the POST request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param content: (optional) Content to include in the request.
        :param data: (optional) Data to include in the request.
        :param files: (optional) Files to include in the request.
        :param json: (optional) JSON data to include in the request.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """

        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().post(
                    url,
                    content=content,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def put(
        self,
        url: str,
        retries: int = 3,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP PUT request with optional retries.

        :param url: The URL to send the PUT request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param content: (optional) Content to include in the request.
        :param data: (optional) Data to include in the request.
        :param files: (optional) Files to include in the request.
        :param json: (optional) JSON data to include in the request.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param auth: (optional) Authentication to use in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().put(
                    url,
                    content=content,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    auth=auth,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def delete(
        self,
        url: str,
        retries: int = 3,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP DELETE request with optional retries.

        :param url: The URL to send the DELETE request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().delete(
                    url,
                    params=params,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                    headers=headers,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def patch(
        self,
        url: str,
        retries: int = 3,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP PATCH request with optional retries.

        :param url: The URL to send the PATCH request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param content: (optional) Content to include in the request.
        :param data: (optional) Data to include in the request.
        :param files: (optional) Files to include in the request.
        :param json: (optional) JSON data to include in the request.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().patch(
                    url,
                    content=content,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def head(
        self,
        url: str,
        retries: int = 3,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP HEAD request with optional retries.

        :param url: The URL to send the HEAD request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().head(
                    url,
                    params=params,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                    headers=headers,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    async def options(
        self,
        url: str,
        retries: int = 3,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> httpxResponse:
        """
        Send an HTTP OPTIONS request with optional retries.

        :param url: The URL to send the OPTIONS request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param params: (optional) Query parameters to include in the request.
        :param headers: (optional) Headers to include in the request.
        :param cookies: (optional) Cookies to include in the request.
        :param follow_redirects: (optional) Whether to follow redirects or use the client's default behavior.
        :param timeout: (optional) The request timeout or use the client's default timeout.
        :param extensions: (optional) Extensions to include in the request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = await super().options(
                    url,
                    params=params,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                    headers=headers,
                )
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )
