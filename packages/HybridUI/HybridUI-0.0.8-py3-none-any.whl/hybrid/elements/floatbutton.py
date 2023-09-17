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
        if not icon == None:
            self.props["icon"] = icon
        if not description == None:
            self.props["description"] = description
        if not tooltip == None:
            self.props["tooltip"] = tooltip
        if not type == None:
            self.props["type"] = type
        if not shape == None:
            self.props["shape"] = shape
        if not onClick == None:
            self.props["onClick"] = onClick
        if not href == None:
            self.props["href"] = href
        if not target == None:
            self.props["target"] = target
        if not badge == None:
            self.props["badge"] = badge
        if not size == None:
            self.props["size"] = size
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
        self.props["shape"] = shape
        self.props["trigger"] = trigger
        self.props["open"] = open
        self.props["onOpenChange"] = onOpenChange
        self.children = content
