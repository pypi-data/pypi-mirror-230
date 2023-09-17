from typing import List, Dict
from ..element import Element


class Switch(Element):
    def __init__(
            self, 

            autoFocus= None,
            checked= None, 
            checkedChildren= None, 
            className= None, 
            defaultChecked= None, 
            disabled= None, 
            loading= None, 
            size= None, 
            onCheckedChildren= None, 
            onChange= None, 
            onClick= None,
            ):
        super().__init__(component='Switch')
        self.children=[]
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if checked is not None:
            self._props["checked"] = checked
        if checkedChildren is not None:
            self._props["checkedChildren"] = checkedChildren
        if className is not None:
            self._props["className"] = className
        if defaultChecked is not None:
            self._props["defaultChecked"] = defaultChecked
        if disabled is not None:
            self._props["disabled"] = disabled
        if loading is not None:
            self._props["loading"] = loading
        if size is not None:
            self._props["size"] = size
        if  onCheckedChildren is not None:
            listner0 = self.on(onCheckedChildren)
            self._props["onCheckedChildren"] = listner0
        if onChange is not None:
            listner1 = self.on(onChange)
            self._props["onChange"] = listner1
        if onClick is not None:
            listner2 = self.on(onClick)
            self._props["onClick"] = listner2
