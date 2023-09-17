from typing import List
from ..element import Element

class Footer(Element):
    """
    Footer component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        style: dict = None,
        className: str = None,
        hasSider: bool = False,

    ):
        super().__init__(component='Footer')
        self._props["style"] = style
        self._props["className"] = className
        self._props["hasSider"] = hasSider
        self.children = content
