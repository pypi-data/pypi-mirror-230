"""HTTP client errors."""
import io
import json
import re
import typing as t

from requests.exceptions import *  # noqa: F403

__all__ = ["ClientError", "NotFound", "ServerError"]


class ClientError(HTTPError):  # noqa: F405
    """The server returned a response with 4xx status."""


class NotFound(ClientError):
    """The server returned a response with 404 status."""


class ServerError(HTTPError):  # noqa: F405
    """The server returned a response with 5xx status."""


def request_exception_getattr(self, name: str):
    """Proxy the response and the request attributes for convenience."""
    # TODO try to subclass requests exceptions in order to enable type-hinting
    # eg. add py.typed after refact so that downstream users can mypy .status_code
    try:
        return getattr(self.response, name)
    except AttributeError:
        pass
    try:
        return getattr(self.request, name)
    except AttributeError:
        pass
    raise AttributeError(f"{type(self).__name__} has no attribute {name!r}")


def request_exception_str(self) -> str:  # pragma: no cover
    """Return the string representation of a RequestException."""
    request = self.request or self.response.request
    return f"{request.method} {request.url} - {self.args[0]}"


def connection_error_str(self) -> str:
    """Return the string representation of a ConnectionError."""
    request = self.request or self.response.request
    msg = str(self.args[0])
    if "Errno" in msg:
        msg = re.sub(r".*(\[[^']*).*", r"\1", msg)
    if "read timeout" in msg:
        msg = re.sub(r'.*: ([^"]*).*', r"\1", msg)
    return f"{request.method} {request.url} - {msg}"


def http_error_str(self) -> str:
    """Return the string representation of an HTTPError."""
    request = self.request or self.response.request
    msg = (
        f"{request.method} {self.response.url} - "
        f"{self.response.status_code} {self.response.reason}"
    )
    if self.response.history:
        hist = "\n".join(
            f"{response.status_code} - {truncate(response.url, 80)}"
            for response in self.response.history
        )
        msg = f"{hist}\n{msg}"
    # capture the request headers
    if request.headers:
        headers = {}
        ignored = r"Accept|Connection|Content-Length"
        for header, value in request.headers.items():
            if header.lower() == "authorization" and " " in value:
                kind = value.split(" ", maxsplit=1)[0]
                headers[header] = f"{kind} {'*' * 5}"
            elif "auth" in header.lower():
                headers[header] = "*" * 5
            elif not re.match(ignored, header, flags=re.IGNORECASE):
                headers[header] = value
        headers_str = json.dumps(headers, separators=(",", ":"), sort_keys=True)
        msg += f"\nRequest headers: {headers_str}"
    # capture the request body we sent
    request_body = truncate(request.body)
    if request_body:
        join = "\n" if "\n" in request_body else " "
        msg += f"\nRequest body:{join}{request_body}"
    # add anything the server had to say about the problem
    response_content = truncate(self.response.content)
    if response_content:
        join = "\n" if "\n" in response_content else " "
        msg += f"\nResponse body:{join}{response_content}"
    return msg


def json_error_str(self) -> str:
    """Return the string representation of an InvalidJSONError."""
    request = self.request or self.response.request
    msg = f"{request.method} {self.response.url} - invalid JSON"
    if self.response.content:
        msg += f" response: {truncate(self.response.content, 20)}"
    return msg


def truncate(data: t.Union[t.IO, bytes, str, None], max_length: int = 256) -> str:
    """Return payload truncated to the specified length as a string."""
    if not data:
        return ""
    name = getattr(data, "name", None)
    if name:  # data=open(file)
        return f"file://{name}"
    if isinstance(data, io.BytesIO):
        data = data.getvalue()
    try:
        data_str = data.decode()  # type: ignore
    except (AttributeError, UnicodeDecodeError):
        data_str = str(data)
    if len(data_str) > max_length:
        data_str = data_str[: max_length - 3].rstrip() + "..."
    return data_str.rstrip()
