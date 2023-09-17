from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Affix(Element):
    def __init__(
        self,
        content: List[Element] = None,
        offsetTop: int = None,
        offsetBottom: int = None,
    ):
        super().__init__(component='Affix')
        self._props["offsetTop"] =offsetTop
        self._props["offsetBottom"] =offsetBottom
        self.children = content
