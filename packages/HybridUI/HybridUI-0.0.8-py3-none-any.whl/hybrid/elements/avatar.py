from typing import List, Union
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Avatar(Element):
    """
    alt	
    gap	
    icon	
    shape	
    size	
    src	
    srcSet	
    draggable	
    crossOrigin	
    onError		

    Avatar.Group 
    Property	
    maxCount	
    maxPopoverPlacement	
    maxPopoverTrigger	
    maxStyle		
    size	
    shape	
    
    """
    def __init__(
        self,
        content: List[Element] = None,
        size: Union[str, int] = "default",
        src: str = "",
        alt: str = "",
        gap=None,
        icon=None,	
        shape=None,		
        srcSet=None,	
        draggable=None,	
        crossOrigin=None,	
        onError=None,		
    ):
        super().__init__(component='Alert')
        if size is not None:
            self._props["size"] = size
        if src is not None:
            self._props["src"] = src
        if alt is not None:
            self._props["alt"] = alt
        if gap is not None:
            self._props["gap"] = gap
        if icon is not None:
            self._props["icon"] = icon
        if shape is not None:
            self._props["shape"] = shape
        if srcSet is not None:
            self._props["srcSet"] = srcSet
        if draggable is not None:
            self._props["draggable"] = draggable
        if crossOrigin is not None:
            self._props["crossOrigin"] = crossOrigin
        if onError is not None:
            onError_listner = self.on(onError)
            self._props["onError"] = onError_listner
        self.children = content




class AvatarGroup(Element):
    """
    Avatar.Group 
    Property	
    maxCount	
    maxPopoverPlacement	
    maxPopoverTrigger	
    maxStyle		
    size	
    shape	
    
    """
    def __init__(
        self,
        content: List[Element] = None,
        size: Union[str, int] = "default",
        src: str = "",
        alt: str = "",
        gap=None,
        icon=None,	
        shape=None,		
        srcSet=None,	
        draggable=None,	
        crossOrigin=None,	
        onError=None,		
    ):
        super().__init__(component='AvatarGroup')
        if size is not None:
            self._props["size"] = size
        if src is not None:
            self._props["src"] = src
        if alt is not None:
            self._props["alt"] = alt
        if gap is not None:
            self._props["gap"] = gap
        if icon is not None:
            self._props["icon"] = icon
        if shape is not None:
            self._props["shape"] = shape
        if srcSet is not None:
            self._props["srcSet"] = srcSet
        if draggable is not None:
            self._props["draggable"] = draggable
        if crossOrigin is not None:
            self._props["crossOrigin"] = crossOrigin
        if onError is not None:
            self._props["onError"] = onError
        self.children = content