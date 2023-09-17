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
        self.props["type"] = type
        self.props["duration"] = duration
        self.props["afterClose"] = afterClose
        self.props["className"] = className
        self.props["icon"] = icon
        self.props["key"] = key
        self.props["style"] = style
        self.props["onClick"] = onClick
        self.props["onClose"] = onClose
