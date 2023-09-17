from __future__ import annotations
from . import globals
import json
import asyncio
from collections import defaultdict, deque
from typing import TYPE_CHECKING, Any, DefaultDict, Deque, Dict, Optional, Tuple

""" globals.app = app = FastAPI()
socket_manager = SocketManager(app=app, mount_location='/hybrid/', json=json)
globals.sio=sio=socket_manager._sio """

ClientId = str
ElementId = int
MessageType = str
Message = Tuple[ClientId, MessageType, Any]

#update_queue: DefaultDict[ClientId, Dict[ElementId, Optional[Element]]] = defaultdict(dict)
message_queue: Deque[Message] = deque()

def enqueue_message(message_type: MessageType, data: Any, target_id: ClientId= None) -> None:
    message_queue.append((target_id, message_type, data))

async def _emit(message_type: MessageType, data: Any, target_id: ClientId = None) -> None:
    await globals.sio.emit(message_type, data, room=target_id)



async def loop() -> None:
    while True:
        if not  message_queue:
            await asyncio.sleep(0.0001)
            continue

        coros = []
        try:
            """ for client_id, elements in update_queue.items():
                data = {
                    element_id: None if element is None else element._to_dict()  # pylint: disable=protected-access
                    for element_id, element in elements.items()
                }
                coros.append(_emit('update', data, client_id))
            update_queue.clear() """

            for target_id, message_type, data in message_queue:
                coros.append(_emit(message_type, data, target_id))
            message_queue.clear()

            for coro in coros:
                try:
                    await coro
                except Exception as e:
                    globals.handle_exception(e)
        except Exception as e:
            globals.handle_exception(e)
            await asyncio.sleep(0.1)
