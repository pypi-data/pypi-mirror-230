from typing import List, Dict
from ..element import Element

from typing import List, Dict
from ..element import Element

class Tag(Element):
    """
    
    Example Usage:
    tag = Tag(
        content="Hello Tag",
        color="blue",
        icon=my_custom_icon,
        bordered=True,
        onClose=my_close_callback,
    )
    """
    def __init__(
            self, 
            content= None,
            closeIcon= None,
            color= None,
            icon= None,
            bordered= None,
            onClose= None,
            ):
        super().__init__(component='Tag')
        self.children = content
        if closeIcon is not None:
            self._props["closeIcon"] = closeIcon
        if color is not None:
            self._props["color"] = color
        if icon is not None:
            self._props["icon"] = icon
        if bordered is not None:
            self._props["bordered"] = bordered
        if onClose is not None:
            listner = self.on(onClose)
            self._props["onClose"] = listner
