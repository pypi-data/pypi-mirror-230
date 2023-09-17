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
        self.props["title"] = title
        self.props["align"] = align
        self.props["arrow"] = arrow
        self.props["autoAdjustOverflow"] = autoAdjustOverflow
        self.props["color"] = color
        self.props["defaultOpen"] = defaultOpen
        self.props["destroyTooltipOnHide"] = destroyTooltipOnHide
        self.props["getPopupContainer"] = getPopupContainer
        self.props["mouseEnterDelay"] = mouseEnterDelay
        self.props["mouseLeaveDelay"] = mouseLeaveDelay
        self.props["overlayClassName"] = overlayClassName
        self.props["overlayStyle"] = overlayStyle
        self.props["overlayInnerStyle"] = overlayInnerStyle
        self.props["placement"] = placement
        self.props["trigger"] = trigger
        self.props["open"] = open
        self.props["zIndex"] = zIndex
        self.props["onOpenChange"] = onOpenChange
        self.props["position"] = position
