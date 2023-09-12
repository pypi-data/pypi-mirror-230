"""Flywheel HTTP API Client."""
from importlib.metadata import version

from .client import FWClient
from .config import FWClientConfig
from .errors import (
    ClientError,
    ConnectionError,
    NotFound,
    ServerError,
)

__version__ = version(__name__)
__all__ = [
    "FWClient",
    "FWClientConfig",
    "ConnectionError",
    "ClientError",
    "NotFound",
    "ServerError",
]
