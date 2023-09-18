from __future__ import annotations

from typing import Union

from .constants import valid_methods

from httpx import AsyncClient, Client

def validate_client(
    client: Union[Client, AsyncClient] = None
) -> Union[Client, AsyncClient]:
    if not client:
        raise ValueError("Missing client to evaluate")

    if not isinstance(client, Client) and not isinstance(client, AsyncClient):
        raise TypeError(
            f"Invalid type for client: {type(client)}. Must be one of [{Client}, {AsyncClient}]"
        )

    return client


def validate_method(method: str = None) -> str:
    """Validate HTTP method."""
    if not method:
        raise ValueError("Missing method to evaluate")

    if method not in valid_methods:
        raise TypeError(f"Invalid method: {method}. Must be one of {valid_methods}")

    return method


def validate_headers(headers: dict[str, str] = None) -> dict[str, str]:
    if not headers:
        raise ValueError("Missing headers to evaluate")

    if not isinstance(headers, dict):
        raise TypeError(
            f"Invalid type for headers: ({type(headers)}). Must be dict[str, str]"
        )

    return headers
