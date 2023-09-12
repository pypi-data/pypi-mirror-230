"""Flywheel client errors."""
from fw_http_client import ClientError, NotFound, ServerError
from requests.exceptions import *  # noqa F403

__all__ = ["ClientError", "NotFound", "ServerError"]
