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
        self.props["style"] = style
        self.props["className"] = className
        self.props["hasSider"] = hasSider
        self.children = content
