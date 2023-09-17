from typing import List
from ..element import Element


class AnchorItem:
    """


    AnchorItem-:

    Property	
    key	
    href			
    target	
    title			
    children		
    replace	
    
    """
    def __init__(
            self,
            key,
            href,			
            target,	
            title,			
            children,		
            replace,	
            ) -> None:
        pass

class Anchor(Element):
    """
    Anchor:


    affix		
    bounds	
    getContainer	
    getCurrentAnchor		
    offsetTop	
    showInkInFixed	
    targetOffset	
    onChange	
    onClick
    items	
    direction	
    replace	


    """

    def __init__(
        self,
        content: List[Element] = None,
        offsetTop = None,
        offsetBottom = None,
        affix = None,		
        bounds = None,
        getContainer = None,	
        getCurrentAnchor = None,			
        showInkInFixed = None,
        targetOffset = None,	
        onChange = None,	
        onClick = None,
        items = None,
        direction = None,	
        replace	= None
    ):
        super().__init__(component='Anchor')
        self.children = content
        if offsetTop is not None:
            self._props["offsetTop"] = offsetTop
        if offsetBottom is not None:
            self._props["offsetBottom"] = offsetBottom
        if affix is not None:
            self._props["affix"] = affix
        if bounds is not None:
            self._props["bounds"] = bounds
        if getContainer is not None:
            self._props["getContainer"] = getContainer
        if getCurrentAnchor is not None:
            self._props["getCurrentAnchor"] = getCurrentAnchor
        if showInkInFixed is not None:
            self._props["showInkInFixed"] = showInkInFixed
        if targetOffset is not None:
            self._props["targetOffset"] = targetOffset
        if onChange is not None:
            self._props["onChange"] = onChange
        if onClick is not None:
            self._props["onClick"] = onClick
        if items is not None:
            self._props["items"] = items
        if direction is not None:
            self._props["direction"] = direction
        if replace is not None:
            self._props["replace"] = replace
        