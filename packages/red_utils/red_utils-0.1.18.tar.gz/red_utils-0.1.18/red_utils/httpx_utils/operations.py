from __future__ import annotations

from .constants import (
    default_headers,
    valid_methods,
)
from .validators import validate_client, validate_headers, validate_method

import httpx

from httpx import Client

def merge_headers(
    original_headers: dict[str, str] = default_headers,
    update_vals: dict[str, str] = None,
) -> dict[str, str]:
    """Merge header dicts into new headers dict."""
    validate_headers(original_headers)
    validate_headers(update_vals)

    try:
        _headers: dict = {**update_vals, **original_headers}

    except Exception as exc:
        raise Exception(f"Unhandled exception merging header dicts. Details: {exc}")

    return _headers


def update_headers(
    original_headers: dict[str, str] = default_headers,
    update_vals: dict[str, str] = None,
) -> dict[str, str]:
    validate_headers(original_headers)
    validate_headers(update_vals)

    try:
        ## Create a copy of original_headers to update
        new_headers: dict[str, str] = original_headers.copy()
        ## Update new_headers with update_vals dict
        new_headers.update(update_vals)

        return new_headers

    except Exception as exc:
        raise Exception(f"Unhandled exception updating headers. Details: {exc}")


def get_req_client(
    headers: dict | None = default_headers, timeout: int | None = None
) -> httpx.Client:
    """Return a customized HTTPX client."""
    _client: Client = Client(headers=headers, timeout=timeout)

    validate_client(_client)

    return _client


def make_request(
    client: Client = None,
    url: str = None,
    method: str = "GET",
    headers: dict = None,
    timeout: int | None = None,
    data: dict | None = None,
) -> httpx.Response:
    """Make a request with HTTPX."""
    validate_method(method)

    if not client:
        print(
            f"[HTTPX] [WARNING] No request client passed to make_request() function. Getting default client."
        )

        client = get_req_client(headers=headers, timeout=timeout)

    validate_client(client=client)

    if not isinstance(client, Client):
        raise TypeError(
            f"Invalid type for client: {type(client)}. Must be of type {type(Client)}"
        )

    if not url:
        raise ValueError("Missing request URL")

    if not isinstance(url, str):
        raise TypeError(f"Invalid type for request URL: {type(url)}")

    if timeout:
        if not isinstance(timeout, int):
            raise TypeError(f"Invalid type for timeout: {type(timeout)}")

    try:
        ## Determine type of request to make
        match method:
            case "GET":
                client = get_req_client(headers=headers, timeout=timeout)

                res = client.get(url=url)

            case _:
                raise ValueError(f"Invalid method: {method}")

        return res

    except Exception as exc:
        raise Exception(f"Unhandled exception creating request client. Details: {exc}")
