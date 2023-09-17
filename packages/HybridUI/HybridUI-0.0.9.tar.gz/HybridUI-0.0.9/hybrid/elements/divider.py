from typing import List, Optional
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Divider(Element):
    """
    Divider:

    children
    className
    dashed
    orientation
    orientationMargin
    plain
    style
    type
    """
    def __init__(
        self,
        content: List[Element] = None,
        type: str = None,
        dashed: bool = None,
        orientation: str = None,
        className: str = None,
        orientationMargin: int = None,
        plain: bool = None,
        style: dict = None,
        children_=None,
    ):
        super().__init__(component='Divider')
        self.children = content
        
        if type is not None:
            self._props["type"] = type
        if dashed is not None:
            self._props["dashed"] = dashed
        if orientation is not None:
            self._props["orientation"] = orientation
        if className is not None:
            self._props["className"] = className
        if orientationMargin is not None:
            self._props["orientationMargin"] = orientationMargin
        if plain is not None:
            self._props["plain"] = plain
        if style is not None:
            self._props["style"] = style
        if children_ is not None:
            self._props["children_"] = children_
