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
        self._props["arrow"] = arrow
        self._props["autoAdjustOverflow"] = autoAdjustOverflow
        self._props["autoFocus"] = autoFocus
        self._props["disabled"] = disabled
        self._props["destroyPopupOnHide"] = destroyPopupOnHide
        self._props["dropdownRender"] = dropdownRender
        self._props["getPopupContainer"] = getPopupContainer
        self._props["menu"] = menu
        self._props["overlayClassName"] = overlayClassName
        self._props["overlayStyle"] = overlayStyle
        self._props["placement"] = placement
        self._props["trigger"] = trigger
        self._props["open"] = open
        self._props["onOpenChange"] = onOpenChange
        self.children= content
        self._props["overlay"] = overlay
        self._props["trigger"] = trigger

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
        self._props["buttonsRender"] = buttonsRender
        self._props["loading"] = loading
        self._props["danger"] = danger
        self._props["icon"] = icon
        self._props["size"] = size
        self._props["type"] = type
        self._props["onClick"] = onClick
        self.children = content
        self._props["overlay"] = overlay
        self._props["trigger"] = trigger
