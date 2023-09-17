import uuid
from page import Page
import time
from typing import Dict, Optional, Any
from . import globals
from pathlib import Path
import asyncio
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union,Literal
from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from .element import Element
from .embedded_encoder import ElementJSONEncoder
import json

#if TYPE_CHECKING:
    #from .page import page

templates = Jinja2Templates(Path(__file__).parent / 'templates')


class Client:
    def __init__(self, page: 'Page', *, shared: bool = False) -> None:
        self.id = str(uuid.uuid4())
        self.created = time.time()
        globals.clients[self.id] = self

        self.elements: Dict[int, Element] = {}
        self.next_element_id: int = 0
        self.is_waiting_for_connection: bool = False
        self.is_waiting_for_disconnect: bool = False
        self.environ: Optional[Dict[str, Any]] = None
        self.shared = shared
        self.on_air = False

        with Element('div', _client=self, ) as self.layout:
            with Element('Layout') as self.page_container:
                with Element('Content'):
                    self.content = Element('div')
        
        self.connect_handlers: List[Union[Callable[..., Any], Awaitable]] = []
        self.disconnect_handlers: List[Union[Callable[..., Any], Awaitable]] = []

    @property
    def ip(self) -> Optional[str]:
        """Return the IP address of the client, or None if the client is not connected."""
        return self.environ['asgi.scope']['client'][0] if self.has_socket_connection else None

    @property
    def has_socket_connection(self) -> bool:
        """Return True if the client is connected, False otherwise."""
        return self.environ is not None

    def __enter__(self):
        self.content.__enter__()
        return self

    def __exit__(self, *_):
        self.content.__exit__()

    def build_response(self, request: Request, status_code: int = 200) -> Response:
        prefix = request.headers.get('X-Forwarded-Prefix', request.scope.get('root_path', ''))
    
        socket_io_js_extra_headers: Dict = {}
        socket_io_js_transports: List[Literal['websocket', 'polling']] = ['websocket', 'polling']
        client_id = str(1)
        elements = json.dumps({id: element.as_dict() for id, element in self.elements.items()}, cls= ElementJSONEncoder)
        data = {
                'query': client_id,
                'prefix': prefix,
                'config': elements,
                'socket_io_js_extra_headers': socket_io_js_extra_headers,
                'socket_io_js_transports': socket_io_js_transports,
        }

        return data

    async def connected(self, timeout: float = 3.0, check_interval: float = 0.1) -> None:
        """Block execution until the client is connected."""
        self.is_waiting_for_connection = True
        deadline = time.time() + timeout
        while not self.has_socket_connection:
            if time.time() > deadline:
                raise TimeoutError(f'No connection after {timeout} seconds')
            await asyncio.sleep(check_interval)
        self.is_waiting_for_connection = False

    async def disconnected(self, check_interval: float = 0.1) -> None:
        """Block execution until the client disconnects."""
        if not self.has_socket_connection:
            await self.connected()
        self.is_waiting_for_disconnect = True
        while self.id in globals.clients:
            await asyncio.sleep(check_interval)
        self.is_waiting_for_disconnect = False
