from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Space(Element):
    def __init__(self, content= None, align= None, direction= None, size= None, split= None, wrap= None):
        super().__init__(component='Space')
        self.children = content
        if align is not None:
            self._props["align"] = align
        if direction is not None:
            self._props["direction"] = direction
        if size is not None:
            self._props["size"] = size
        if split is not None:
            self._props["split"] = split
        if wrap is not None:
            self._props["wrap"] = wrap


class SpaceCompact(Element):
    def __init__(self, content= None, block= None,direction= None,size= None,styles= None,classNames= None,item= None):
        super().__init__(component='Space')
        self.children = content
        if block is not None:
            self._props["block"] = block
        if direction is not None:
            self._props["direction"] = direction
        if size is not None:
            self._props["size"] = size
        if styles is not None:
            self._props["styles"] = styles
        if classNames is not None:
            self._props["classNames"] = classNames
        if item is not None:
            self._props["item"] = item
