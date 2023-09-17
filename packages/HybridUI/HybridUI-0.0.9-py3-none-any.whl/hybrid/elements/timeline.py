from typing import List, Dict, Any
from ..element import Element


class Items:
    def __init__(self, color= None, dot=None, closeIcon= None, label=None, children=None, position=None):
        

        if color is not None:
            self.color = color
        if dot is not None:
            self.dot = dot
        if closeIcon is not None:
            self.closeIcon= closeIcon
        if children is not None:
            self.children = children
        if position is not None:
            self.position= position
        if label is not None:
            self.label= label

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__



class Timeline(Element):
    """
    Example Usage:
    timeline = Timeline(
        mode='left',
        pending=False,
        pendingDot=my_pending_dot,
        reverse=False,
        items=[
            Timeline.Items(color='blue', label='Label 1', children='Content 1'),
            Timeline.Items(color='green', label='Label 2', children='Content 2'),
        ]
    )
    """
#mode, pending, pendingDot, reverse, items, Buttontype, Buttonstyle, Buttononclick, Buttonchildren
    def __init__(
            self,  
            pending: bool = None, 
            mode= None, 
            pendingDot= None, 
            reverse= None,
            items = None, 
            Buttontype= None, 
            Buttonstyle= None, 
            Buttononclick= None, 
            Buttonchildren= None):
        super().__init__(component='Timeline')

        if mode is not None:
            self._props["mode"] = mode
        if pending is not None:
            self._props["pending"] = pending
        if pendingDot is not None:
            self._props["pendingDot"] = pendingDot
        if reverse is not None:
            self._props["reverse"] = reverse
        if items is not None:
            self._props["items"] = items
        #________________
        if Buttontype is not None:
            self._props["Buttontype"] = Buttontype
        if Buttonstyle is not None:
            self._props["Buttonstyle"] = Buttonstyle
        if Buttonchildren is not None:
            self._props["Buttonchildren"] = Buttonchildren
        if Buttononclick is not None:
            listner = self.on(Buttononclick)
            self._props["Buttononclick"] = listner

