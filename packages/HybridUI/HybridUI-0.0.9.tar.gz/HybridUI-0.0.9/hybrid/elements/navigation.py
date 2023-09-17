from typing import List, Optional, Union, Literal
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Navigation(Element):

    def __init__(
        self,
        content: List[Element] = None,
        mode: Literal["horizontal", "vertical"] = "horizontal",
        theme: Literal["light", "dark"] = "light",
    ):
        super().__init__(component='Navigation')
        self._props["mode"] = mode
        self._props["theme"] = theme
