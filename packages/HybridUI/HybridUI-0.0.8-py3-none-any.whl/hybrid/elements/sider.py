from typing import List
from ..element import Element

class Sider(Element):
    def __init__(
        self,
        content: List[Element] = None,
        style: dict = None,
        className: str = None,
        hasSider: bool = False,
        breakpoint= None,
        collapsed= None,
        collapsedWidth= None,
        collapsible= None,
        defaultCollapsed = None,
        reverseArrow= None,
        theme= None,
        trigger= None,
        width= None,
        zeroWidthTriggerStyle= None,
        onBreakpoint = None,
        onCollapse= None,
        # Add other props here
    ):
        super().__init__(component='Sider')
        self.children = content
        if hasSider is not None:
            self._props["hasSider"] = hasSider
        if breakpoint is not None:
            self._props["breakpoint"] = breakpoint
        if className is not None:
            self._props["className"] = className
        if collapsed is not None:
            self._props["collapsed"] = collapsed
        if collapsedWidth is not None:
            self._props["collapsedWidth"] = collapsedWidth
        if collapsible is not None:
            self._props["collapsible"] = collapsible
        if defaultCollapsed is not None:
            self._props["defaultCollapsed"] = defaultCollapsed
        if reverseArrow is not None:
            self._props["reverseArrow"] = reverseArrow
        if style is not None:
            self._props["style"] = style
        if theme is not None:
            self._props["theme"] = theme
        if trigger is not None:
            self._props["trigger"] = trigger
        if width is not None:
            self._props["width"] = width
        if zeroWidthTriggerStyle is not None:
            self._props["zeroWidthTriggerStyle"] = zeroWidthTriggerStyle
        if onBreakpoint is not None:
            self._props["onBreakpoint"] = onBreakpoint
        if onCollapse is not None:
            self._props["onCollapse"] = onCollapse

