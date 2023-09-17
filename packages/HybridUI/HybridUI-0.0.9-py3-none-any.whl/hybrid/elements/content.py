from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Content(Element):
    """
    Layout:

    className
    hasSider
    style
    """
    def __init__(
        self,
        content: List[Element] = None,
        style: dict = None,
        className: str = None,
        
    ):
        super().__init__(component='Content')
        self.children = content
        if style is not None:
            self._props["style"] = style
        if className is not None:
            self._props["className"] = className
        
