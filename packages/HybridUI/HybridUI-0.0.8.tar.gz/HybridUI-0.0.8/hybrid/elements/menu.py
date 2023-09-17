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
        self.props["mode"] = mode
        self.props["expandIcon"] = expandIcon
        self.props["forceSubMenuRender"] = forceSubMenuRender
        self.props["inlineCollapsed"] = inlineCollapsed
        self.props["inlineIndent"] = inlineIndent
        self.props["items"] = items
        self.props["multiple"] = multiple
        self.props["overflowedIndicator"] = overflowedIndicator
        self.props["selectable"] = selectable
        self.props["style"] = style
        self.props["subMenuCloseDelay"] = subMenuCloseDelay
        self.props["subMenuOpenDelay"] = subMenuOpenDelay
        self.props["triggerSubMenuAction"] = triggerSubMenuAction
        self.props["theme"] = theme
        self.props["defaultSelectedKeys"] = defaultSelectedKeys
        self.props["defaultOpenKeys"] = defaultOpenKeys
        self.props["selectedKeys"] = selectedKeys
        self.props["openKeys"] = openKeys
        self.props["onSelect"] = onSelect
        self.props["onOpenChange"] = onOpenChange
        self.props["onClick"] = onClick
        self.props["onDeselect"] =onDeselect 
