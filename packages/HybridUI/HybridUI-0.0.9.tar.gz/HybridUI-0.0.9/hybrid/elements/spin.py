from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert
class Spin(Element):

    def __init__(self, content: List[Element] = None,delay= None,indicator= None, size= None,spinning= None,tip= None,wrapperClassName= None):
        super().__init__(component='Spin')
        self.children = content
        self._props["delay"] = delay
        self._props["indicator"] = indicator
        self._props["size"] = size
        self._props["spinning"] = spinning
        self._props["tip"] = tip
        self._props["wrapperClassName"] = wrapperClassName
