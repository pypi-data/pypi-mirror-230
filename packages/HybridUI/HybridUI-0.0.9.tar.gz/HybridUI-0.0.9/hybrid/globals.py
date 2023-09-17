from __future__ import annotations
import asyncio
import inspect
import logging
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Iterator, List, Literal, Optional, Set, Union
from fastapi import FastAPI
from socketio import AsyncServer
from uvicorn import Server
from . import background_tasks
update_component = []

if TYPE_CHECKING:
    from .client import Client



class State(Enum):
    STOPPED = 0
    STARTING = 1
    STARTED = 2
    STOPPING = 3

layout = []
app: FastAPI 
sio: AsyncServer
server: Server
loop: Optional[asyncio.AbstractEventLoop] = None
log: logging.Logger = logging.getLogger('hybrid')
state: State = State.STOPPED
ui_run_has_been_called: bool = False
optional_features: Set[str] = set()

reload: bool
title: str
viewport: str
favicon: Optional[Union[str, Path]]
dark: Optional[bool]
binding_refresh_interval: float
tailwind: bool
prod_js: bool
endpoint_documentation: Literal['none', 'internal', 'page', 'all'] = 'none'
socket_io_js_query_params: Dict = {}
socket_io_js_extra_headers: Dict = {}
socket_io_js_transports: List[Literal['websocket', 'polling']] = ['websocket', 'polling']
_socket_id: Optional[str] = None
clients: Dict[str, Client] = {}
index_client: Client
page_routes: Dict[Callable[..., Any], str] = {}
startup_handlers: List[Union[Callable[..., Any], Awaitable]] = []
shutdown_handlers: List[Union[Callable[..., Any], Awaitable]] = []
connect_handlers: List[Union[Callable[..., Any], Awaitable]] = []
disconnect_handlers: List[Union[Callable[..., Any], Awaitable]] = []
exception_handlers: List[Callable[..., Any]] = [log.exception]


def get_task_id() -> int:
    try:
        return id(asyncio.current_task())
    except RuntimeError:
        return 0






def get_client() -> Client:
    return 1


@contextmanager
def socket_id(id_: str) -> Iterator[None]:
    global _socket_id  # pylint: disable=global-statement
    _socket_id = id_
    yield
    _socket_id = None


def handle_exception(exception: Exception) -> None:
    for handler in exception_handlers:
        result = handler() if not inspect.signature(handler).parameters else handler(exception)
        if isinstance(result, Awaitable):
            background_tasks.create(result)

