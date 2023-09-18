from __future__ import annotations

from .tag_definitions import tags_metadata

default_allow_credentials: bool = True
default_allowed_origins: list[str] = ["*"]
default_allowed_methods: list[str] = ["*"]
default_allowed_headers: list[str] = ["*"]


## Route to openapi docs. This returns the docs site as a JSON object
#  If you set this to the same route as docs (i.e. /docs), you will only
#  get the openapi JSON response, no Swagger docs.
default_openapi_url: str = "/docs/openapi"

default_api_str: str = "/api/v1"

_ts: str = "[{time:YYYY-MM-DD_HH:mm:ss}]"
_level: str = "[{level}]"
_name_line: str = "[{name}:{line}]"
_msg: str = "{message}"
default_color_fmt: str = f"<green>{_ts}</green> <level>{_level}</level> > <level>{_name_line}</level>: {_msg}"
