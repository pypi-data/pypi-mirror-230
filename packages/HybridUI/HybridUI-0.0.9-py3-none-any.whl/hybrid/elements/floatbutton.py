from typing import List, Callable
from ..element import Element

class FloatButton(Element):
    """
    FloatButton component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        onClick: Callable = None,
        type: str = "primary",
        shape: str = "circle",
        icon: str = None,
        size: str = "default",
        href: str = None,
        target: str = None,
        badge: str = None,
        description = None,
        tooltip=None
     
    ):
        super().__init__(component='FloatButton')
        if icon is not None:
            self._props["icon"] = icon
        if description is not None:
            self._props["description"] = description
        if tooltip is not None:
            self._props["tooltip"] = tooltip
        if type is not None:
            self._props["type"] = type
        if shape is not None:
            self._props["shape"] = shape
        if onClick is not None:
            self._props["onClick"] = onClick
        if href is not None:
            self._props["href"] = href
        if target is not None:
            self._props["target"] = target
        if badge is not None:
            self._props["badge"] = badge
        if size is not None:
            self._props["size"] = size
        self.children = content

class FloatButtonGroup(Element):
    """
    FloatButtonGroup component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        shape: str = "circle",
        trigger: str = "click",
        open: bool = False,
        onOpenChange: Callable = None,

    ):
        super().__init__(component='FloatButtonGroup')
        if shape is not None:    
            self._props["shape"] = shape
        if trigger is not None:    
            self._props["trigger"] = trigger
        if open is not None:    
            self._props["open"] = open
        if onOpenChange is not None:    
            self._props["onOpenChange"] = onOpenChange
        self.children = content
