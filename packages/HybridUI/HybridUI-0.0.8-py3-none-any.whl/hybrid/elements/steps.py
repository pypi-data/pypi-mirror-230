from typing import List, Dict
from ..element import Element


class Steps(Element):
    def __init__(
            self, 
            content = None,
            items= None, 
            onChange= None, 
            type= None, 
            status= None, 
            size= None, 
            responsive= None, 
            progressDot= None, 
            percent= None, 
            labelPlacement= None, 
            initial= None, 
            direction= None, 
            current= None, 
            className= None):
        
        
        super().__init__(component='Steps')
        self.children =content
        if className is not None:
            self._props["className"] = className
        if current is not None:
            self._props["current"] = current
        if direction is not None:
            self._props["direction"] = direction
        if initial is not None:
            self._props["initial"] = initial
        if labelPlacement is not None:
            self._props["labelPlacement"] = labelPlacement
        if percent is not None:
            self._props["percent"] = percent
        if progressDot is not None:
            self._props["progressDot"] = progressDot
        if responsive is not None:
            self._props["responsive"] = responsive
        if size is not None:
            self._props["size"] = size
        if status is not None:
            self._props["status"] = status
        if type is not None:
            self._props["type"] = type
        if onChange is not None:
            self._props["onChange"] = onChange
        if items is not None:
            self._props["items"] = items
