"""Prod-ready HTTP client with timeout and retries by default."""
import functools
from importlib.metadata import version

from pydantic.json import pydantic_encoder
from requests.compat import json  # type: ignore
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    InvalidJSONError,  # type: ignore
    RequestException,
)

from . import errors
from .client import HttpClient, dump_useragent, load_useragent
from .config import AnyAuth, HttpConfig
from .errors import ClientError, NotFound, ServerError

__version__ = version(__name__)
__all__ = [
    "AnyAuth",
    "HttpClient",
    "HttpConfig",
    "dump_useragent",
    "load_useragent",
    "errors",
    "ConnectionError",
    "ClientError",
    "NotFound",
    "RequestException",
    "ServerError",
]

# patch the exceptions for more useful default error messages
RequestException.__getattr__ = errors.request_exception_getattr  # type: ignore
RequestException.__str__ = errors.request_exception_str  # type: ignore
ConnectionError.__str__ = errors.connection_error_str  # type: ignore
HTTPError.__str__ = errors.http_error_str  # type: ignore
InvalidJSONError.__str__ = errors.json_error_str  # type: ignore

# patch json.dumps to use the same encoder as pydantic
json.dumps = functools.partial(json.dumps, default=pydantic_encoder)
