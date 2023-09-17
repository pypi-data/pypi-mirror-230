from typing import List, Union, Literal, Callable, Optional
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Menu(Element):
    def __init__(
        self,
        content: List[Element] = None,
        defaultOpenKeys = None,
        defaultSelectedKeys= None,
        expandIcon= None,
        forceSubMenuRender= None,
        inlineCollapsed= None,
        inlineIndent= None,
        items= None,
        mode= None,
        multiple= None,
        openKeys= None,
        overflowedIndicator= None,
        selectable= None,
        selectedKeys= None,
        style= None,
        subMenuCloseDelay= None,
        subMenuOpenDelay= None,
        theme= None,
        triggerSubMenuAction= None,
        onClick= None,
        onDeselect= None,
        onOpenChange= None,
        onSelect= None,
    ):
        super().__init__(component='Menu')
        self.children = content
        if mode is not None:
            self._props["mode"] = mode
        if expandIcon is not None:
            self._props["expandIcon"] = expandIcon
        if forceSubMenuRender is not None:
            self._props["forceSubMenuRender"] = forceSubMenuRender
        if inlineCollapsed is not None:
            self._props["inlineCollapsed"] = inlineCollapsed
        if inlineIndent is not None:
            self._props["inlineIndent"] = inlineIndent
        if items is not None:
            self._props["items"] = items
        if multiple is not None:
            self._props["multiple"] = multiple
        if overflowedIndicator is not None:
            self._props["overflowedIndicator"] = overflowedIndicator
        if selectable is not None:
            self._props["selectable"] = selectable
        if style is not None:
            self._props["style"] = style
        if subMenuCloseDelay is not None:
            self._props["subMenuCloseDelay"] = subMenuCloseDelay
        if subMenuOpenDelay is not None:
            self._props["subMenuOpenDelay"] = subMenuOpenDelay
        if triggerSubMenuAction is not None:
            self._props["triggerSubMenuAction"] = triggerSubMenuAction
        if theme is not None:
            self._props["theme"] = theme
        if defaultSelectedKeys is not None:
            self._props["defaultSelectedKeys"] = defaultSelectedKeys
        if defaultOpenKeys is not None:
            self._props["defaultOpenKeys"] = defaultOpenKeys
        if selectedKeys is not None:
            self._props["selectedKeys"] = selectedKeys
        if openKeys is not None:
            self._props["openKeys"] = openKeys
        if onSelect is not None:
            self._props["onSelect"] = onSelect
        if onOpenChange is not None:
            self._props["onOpenChange"] = onOpenChange
        if onClick is not None:
            self._props["onClick"] = onClick
        if onDeselect is not None:
            self._props["onDeselect"] =onDeselect 
