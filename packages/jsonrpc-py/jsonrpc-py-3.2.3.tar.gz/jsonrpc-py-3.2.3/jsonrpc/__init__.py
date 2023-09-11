"""
Pure zero-dependency JSON-RPC 2.0 implementation.
"""

from typing import Final

from .asgi import ASGIHandler
from .dispatcher import AsyncDispatcher
from .errors import Error, ErrorEnum
from .lifespan import LifespanEvents
from .requests import BatchRequest, Request
from .responses import BatchResponse, Response
from .serializers import JSONSerializer

__all__: Final[tuple[str, ...]] = (
    "ASGIHandler",
    "AsyncDispatcher",
    "BatchRequest",
    "BatchResponse",
    "Error",
    "ErrorEnum",
    "JSONSerializer",
    "LifespanEvents",
    "Request",
    "Response",
)
