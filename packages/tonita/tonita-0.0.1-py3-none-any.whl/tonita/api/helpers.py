"""Contains private helper functions for interfacing with remote API resources.

For users of the Tonita API, it should not be necessary to call these functions
on their own; all valid ways of interfacing with the server have corresponding
public functions in this library that, in turn, call these helpers.
"""

import json
import sys
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

import tonita
from tonita.constants import (
    API_KEY_HTTP_HEADER_FIELD_NAME,
    API_KEY_NAME,
    BASE_URL_NAME,
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    PACKAGE_NAME,
)
from tonita.errors import (
    TonitaBadRequestError,
    TonitaError,
    TonitaInternalServerError,
    TonitaNotImplementedError,
    TonitaUnauthorizedError,
)


def _get_module_var_value(var_name: str) -> Any:
    """Returns the value of the module variable with the specified name."""

    module = sys.modules[PACKAGE_NAME]
    return getattr(module, var_name)


def _resolve_field_value(name: str, value: Optional[str] = None) -> str:
    """Checks that a variable has at least one value and decides which to use.

    For certain variables like API key or corpus ID, it is possible for its
    value to be provided via either a module variable (e.g., `tonita.api_key`)
    or an argument in a function call. This function (1) checks that a value is
    provided at all and then (2) decides which to use.

    If `value` is provided, then it is returned. Otherwise if it is `None`, the
    module variable `tonita.{name}` will be returned. If that is also `None`,
    then an error will be thrown.

    Args:
        name (str):
            The string name of the module variable whose value to resolve. This
            should match the name of the module variable exactly. For example,
            if the module variable is set using `tonita.api_key = "foo"`, then
            `name` should be "api_key".
        value (Optional[str]):
            The value of the variable.

    Returns:
        str:
            The value to use.

    Raises:
        TonitaBadRequestError:
            If no value is found.

    """

    if value is None:
        if name not in vars(tonita) or vars(tonita)[name] is None:
            raise TonitaBadRequestError(
                f"Value for {name} not found. "
                "Please provide it either in the function call or "
                f"by setting `tonita.{name}`."
            )
        else:
            value = vars(tonita)[name]

    return value


def _request(
    method: str,
    url_path: str,
    session: Optional[requests.Session] = None,
    headers: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    data: Optional[Any] = None,
    json_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Makes a request to the server and returns the response as a dict.

    Functions in the client libraries should call this function to interface
    with internal resources.

    Args:
        method (str):
            An HTTP request method (e.g., "GET"). Case-insensitive.
        url_path (str):
            The server path for the request. Will be appended to base URL
            given by the module variables.
        session (Optional[requests.Session]):
            A `requests.Session` object to use for the request. If
            the user does not provide a session, a new one will be created.
        headers (Optional[Dict[str, Any]]):
            Header content for the request. The headers should not contain the
            API key.
        api_key (Optional[str]):
            An API key. If one is provided here, it will take precedence over
            that set via tonita.api_key.
        data (Optional[Any]):
            Data to be sent via POST (e.g., a dict sent as an
            application/json). Will be ignored if the request method is GET.
        json_path (Optional[str]):
            Path to a file to be sent via POST. Will be ignored if the request
            method is GET.

    Returns:
        Dict[str, Any]:
            A dict containing the response data.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaNotImplementedError:
            If a HTTP request method is not implemented.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaError:
            Something else went wrong.
    """

    # Resolve the base URL to use for this API request.
    url_base = _get_module_var_value(var_name=BASE_URL_NAME)

    # If `headers` dict exists, add API key to it; otherwise instantiate it.
    api_key = _resolve_field_value(name=API_KEY_NAME, value=api_key)

    if headers is not None:
        if API_KEY_HTTP_HEADER_FIELD_NAME in headers:
            raise TonitaBadRequestError(
                "API key should be passed in the `api_key` argument or set "
                f"via tonita.{API_KEY_NAME}, not passed through request "
                "headers."
            )

        headers[API_KEY_HTTP_HEADER_FIELD_NAME] = api_key
    else:
        headers = {API_KEY_HTTP_HEADER_FIELD_NAME: api_key}

    # Send request to Tonita servers.
    request_url = urljoin(url_base, url_path)

    request_args = {"url": request_url, "headers": headers}

    if session is None:
        session = requests.Session()

    method = method.lower()
    if method == HTTP_METHOD_GET:
        response = session.get(**request_args)

    elif method == HTTP_METHOD_POST:
        request_args["headers"]["Content-Type"] = "application/json"

        # Check that exactly one of `data` or `json_path` is provided.
        if (data and json_path) or (not data and not json_path):
            raise ValueError(
                "Exactly one of `data` or `json_path` should be provided."
            )

        if data is not None:
            response = session.post(**request_args, json=data)

        if json_path is not None:
            with open(json_path, "r") as f:
                response = session.post(**request_args, json=json.load(f))

    else:
        raise TonitaNotImplementedError(
            f"HTTP request method {method} not implemented."
        )

    # Throw error if applicable.
    if response.status_code != 200:
        response_code_and_text = f"{response.status_code}: {response.text}"

        if response.status_code == 400:
            raise TonitaBadRequestError(response_code_and_text)
        elif response.status_code == 401:
            raise TonitaUnauthorizedError(response_code_and_text)
        elif response.status_code == 500:
            raise TonitaInternalServerError(response_code_and_text)
        else:
            raise TonitaError(response_code_and_text)

    # Return response data as dict.
    return response.json()
