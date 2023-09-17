from typing import List
from ..element import Element

class DropDown(Element):
    """
    Dropdown component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        overlay: Element = None,
        trigger: List[str] = ["hover"],
        arrow = None,
        autoAdjustOverflow=None,
        autoFocus=None,
        disabled=None,
        destroyPopupOnHide=None,
        dropdownRender=None,
        getPopupContainer=None,
        menu=None,
        overlayClassName=None,
        overlayStyle=None,
        placement=None,
        open=None,
        onOpenChange=None
    ):
        super().__init__(component='DropDown')
        self.props["arrow"] = arrow
        self.props["autoAdjustOverflow"] = autoAdjustOverflow
        self.props["autoFocus"] = autoFocus
        self.props["disabled"] = disabled
        self.props["destroyPopupOnHide"] = destroyPopupOnHide
        self.props["dropdownRender"] = dropdownRender
        self.props["getPopupContainer"] = getPopupContainer
        self.props["menu"] = menu
        self.props["overlayClassName"] = overlayClassName
        self.props["overlayStyle"] = overlayStyle
        self.props["placement"] = placement
        self.props["trigger"] = trigger
        self.props["open"] = open
        self.props["onOpenChange"] = onOpenChange
        self.children= content
        self.props["overlay"] = overlay
        self.props["trigger"] = trigger

class DropDownButton(Element):
    """
    Dropdown Button component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        overlay: Element = None,
        trigger: List[str] = ["hover"],
        buttonsRender=None,
        loading=None,
        danger =None,
        icon =None,
        size= None,
        onClick=None,
        type= None
    ):
        super().__init__(component='DropDownButton')
        self.props["buttonsRender"] = buttonsRender
        self.props["loading"] = loading
        self.props["danger"] = danger
        self.props["icon"] = icon
        self.props["size"] = size
        self.props["type"] = type
        self.props["onClick"] = onClick
        self.children = content
        self.props["overlay"] = overlay
        self.props["trigger"] = trigger
