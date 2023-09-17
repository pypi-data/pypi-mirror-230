from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert
class Spin(Element):

    def __init__(self, content: List[Element] = None,delay= None,indicator= None, size= None,spinning= None,tip= None,wrapperClassName= None):
        super().__init__(component='Spin')
        self.children = content
        self.props["delay"] = delay
        self.props["indicator"] = indicator
        self.props["size"] = size
        self.props["spinning"] = spinning
        self.props["tip"] = tip
        self.props["wrapperClassName"] = wrapperClassName
