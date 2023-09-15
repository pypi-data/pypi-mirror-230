from __future__ import annotations
from dataclasses import dataclass, field
from requests import Session
import ua_generator
from typing import *
from ua_generator.useragent import UserAgent
from requests import Response
from requests.exceptions import (
    Timeout,
    ReadTimeout,
    ConnectTimeout,
    ChunkedEncodingError,
)

try:
    from models import SessionMetaData
    from exceptions import RetriesExceeded
except ImportError:
    from ..models import SessionMetaData
    from ..exceptions import RetriesExceeded


@dataclass
class SyncSession(Session):
    proxy: str | None = field(default=None)
    ignore_exceptions: Tuple[Type[Exception]] = field(repr=False, default_factory=tuple)
    user_agent: UserAgent = field(
        init=False, repr=False, default=ua_generator.generate(device="desktop")
    )
    meta_data: SessionMetaData | dict = field(default_factory=SessionMetaData)

    def __post_init__(self):
        """
        Initialize the SyncSession object after the parent class is initialized.

        This method sets the user-agent header, proxies, and converts the meta_data to SessionMetaData if needed.
        """
        super().__init__()
        self.headers["user-agent"] = self.user_agent.text
        if self.proxy is None:
            proxies = None
        else:
            proxies = {
                "http": f"http://{self.proxy}",
                "https": f"http://{self.proxy}",
            }
        self.proxies = proxies
        if not isinstance(self.meta_data, SessionMetaData):
            self.meta_data = SessionMetaData(self.meta_data)

    def get(self, url, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP GET request with optional retries.

        :param url: The URL to send the GET request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying GET request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().get(url, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def post(
        self, url, data: dict = None, json: dict = None, retries: int = 3, **kwargs
    ) -> Response:
        """
        Send an HTTP POST request with optional retries.

        :param url: The URL to send the POST request to.
        :param data: The data to include in the request body as form data.
        :param json: The JSON data to include in the request body.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying POST request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().post(url, data=data, json=json, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def put(self, url, data: dict = None, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP PUT request with optional retries.

        :param url: The URL to send the PUT request to.
        :param data: The data to include in the request body as form data.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying PUT request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().put(url, data=data, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def delete(self, url, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP DELETE request with optional retries.

        :param url: The URL to send the DELETE request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying DELETE request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().delete(url, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def patch(self, url, data: dict = None, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP PATCH request with optional retries.

        :param url: The URL to send the PATCH request to.
        :param data: The data to include in the request body as form data.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying PATCH request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().patch(url, data=data, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def head(self, url, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP HEAD request with optional retries.

        :param url: The URL to send the HEAD request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying HEAD request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().head(url, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )

    def options(self, url, retries: int = 3, **kwargs) -> Response:
        """
        Send an HTTP OPTIONS request with optional retries.

        :param url: The URL to send the OPTIONS request to.
        :param retries: The number of times to retry the request in case of exceptions.
        :param **kwargs: Additional keyword arguments passed to the underlying OPTIONS request.

        :return: The HTTP response object.

        :raises RetriesExceeded: If the maximum number of retries is exceeded.
        """
        ignored_exceptions = []
        for _ in range(retries):
            try:
                r = super().options(url, **kwargs)
                return r
            except self.ignore_exceptions as e:
                ignored_exceptions.append(e)
        raise RetriesExceeded(
            f"Failed request {retries}/{retries} times", retries, ignored_exceptions
        )
