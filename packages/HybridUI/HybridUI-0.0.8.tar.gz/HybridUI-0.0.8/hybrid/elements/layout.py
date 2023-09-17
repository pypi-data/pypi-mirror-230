from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Layout(Element):
    def __init__(
        self,
        content = None,
        style: dict = None,
        className: str = None,
        hasSider=None,
    ):
        super().__init__('Layout')
        self.children =content
        
        if style is not None:
            self._props["style"] =style
        if className is not None:
            self._props["className"] =className
        if hasSider is not None:
            self._props["hasSider"] =hasSider
