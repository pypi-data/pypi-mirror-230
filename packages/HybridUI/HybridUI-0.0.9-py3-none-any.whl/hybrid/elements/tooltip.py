from typing import List, Dict
from ..element import Element



class Tooltip(Element):
    """

    Example Usage:
    tooltip = Tooltip(
        title="Tooltip content",
        align={/* align options */},
        arrow=True,
        autoAdjustOverflow=True,
        # ... (other properties)
    )
    """
    def __init__(
            self, 
            content: List[Element] = None, 
            position: str = "top", 
            title= None, 
            align= None, 
            arrow= None, 
            autoAdjustOverflow= None, 
            color= None, 
            defaultOpen= None, 
            destroyTooltipOnHide= None, 
            getPopupContainer= None, 
            mouseEnterDelay= None,
            mouseLeaveDelay= None, 
            overlayClassName= None, 
            overlayStyle= None,  
            overlayInnerStyle= None, 
            placement= None, 
            trigger= None, 
            open= None, 
            zIndex= None, 
            onOpenChange= None,
            ): 
        super().__init__(component='Tooltip')
        self.children =content
        self._props["title"] = title
        self._props["align"] = align
        self._props["arrow"] = arrow
        self._props["autoAdjustOverflow"] = autoAdjustOverflow
        self._props["color"] = color
        self._props["defaultOpen"] = defaultOpen
        self._props["destroyTooltipOnHide"] = destroyTooltipOnHide
        self._props["getPopupContainer"] = getPopupContainer
        self._props["mouseEnterDelay"] = mouseEnterDelay
        self._props["mouseLeaveDelay"] = mouseLeaveDelay
        self._props["overlayClassName"] = overlayClassName
        self._props["overlayStyle"] = overlayStyle
        self._props["overlayInnerStyle"] = overlayInnerStyle
        self._props["placement"] = placement
        self._props["trigger"] = trigger
        self._props["open"] = open
        self._props["zIndex"] = zIndex
        self._props["onOpenChange"] = onOpenChange
        self._props["position"] = position
