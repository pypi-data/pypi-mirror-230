import os
import sys
from contextvars import ContextVar
from typing import Optional, Callable, Union, TYPE_CHECKING

import requests

from sensenova.version import VERSION

from sensenova.api_resources import (
    Dataset,
    Model,
    FineTune,
    Serving,
    ChatCompletion,
    FinetuneCompletion,
    KnowledgeBase,
    File,
    ChatSession,
    ChatConversation
)
from sensenova.error import APIError, InvalidRequestError, SensenovaError

if TYPE_CHECKING:
    import requests
    from aiohttp import ClientSession

verify_ssl_certs = True
access_key_id = os.environ.get("SENSENOVA_ACCESS_KEY_ID")
secret_access_key = os.environ.get("SENSENOVA_SECRET_ACCESS_KEY")
api_base = os.environ.get("SENSENOVA_API_BASE", "https://api.sensenova.cn/v1")
api_base_file = os.environ.get("SENSENOVA_API_BASE_FILE", "https://file.sensenova.cn/v1")
app_info = None
debug = False
log = None

requestssession: Optional[
    Union["requests.Session", Callable[[], "requests.Session"]]
] = None

aiosession: ContextVar[Optional["ClientSession"]] = ContextVar(
    "aiohttp-session", default=None
)

__version__ = VERSION
__all__ = [
    "APIError",
    "InvalidRequestError",
    "SensenovaError",
    "Dataset",
    "Model",
    "FineTune",
    "Serving",
    "ChatCompletion",
    "FinetuneCompletion",
    "KnowledgeBase"
]
