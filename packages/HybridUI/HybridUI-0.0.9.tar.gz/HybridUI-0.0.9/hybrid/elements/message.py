from typing import List, Union, Literal, Optional, Callable
from ..element import Element



class Message(Element):

    def __init__(
        self,
        content: str = "",
        type=None,
        duration= None,
        onClose = None,
        afterClose = None,
        className = None,
        icon = None,
        key = None,
        style = None,
        onClick = None,
    ):
        super().__init__(component='Message')
        self.children = content
        self._props["type"] = type
        self._props["duration"] = duration
        self._props["afterClose"] = afterClose
        self._props["className"] = className
        self._props["icon"] = icon
        self._props["key"] = key
        self._props["style"] = style
        self._props["onClick"] = onClick
        self._props["onClose"] = onClose
