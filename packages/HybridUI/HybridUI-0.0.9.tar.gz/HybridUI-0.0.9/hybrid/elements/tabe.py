from typing import List
from ..element import Element


class Tabe(Element):
    def __init__(
            self, 
            content: List[Element] = None,
            activeKey= None,
            addIcon = None,
            animated = None,
            centered = None,
            defaultActiveKey = None,
            hideAdd = None,
            items = None,
            moreIcon= None, 
            popupClassName = None,
            renderTabBar = None,
            size = None,
            tabBarExtraContent= None, 
            tabBarGutter = None,
            tabBarStyle = None,
            tabPosition= None, 
            destroyInactiveTabPane= None, 
            type = None,
            onChange = None,
            onEdit = None,
            onTabClick= None, 
            onTabScroll= None,
            
            ):
        super().__init__(component='Tabs')
        self.children = content
        if activeKey is not None:
            self._props["activeKey"] = activeKey
        if addIcon is not None:
            self._props["addIcon"] = addIcon
        if animated is not None:
            self._props["animated"] = animated
        if centered is not None:
            self._props["centered"] = centered
        if defaultActiveKey is not None:
            self._props["defaultActiveKey"] = defaultActiveKey 
        if hideAdd is not None:
            self._props["hideAdd"] = hideAdd 
        if items is not None:
            self._props["items"] = items 
        if moreIcon is not None:
            self._props["moreIcon"] = moreIcon 
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName 
        if renderTabBar is not None:
            self._props["renderTabBar"] = renderTabBar
        if size is not None:
            self._props["size"] = size
        if tabBarExtraContent is not None:
            self._props["tabBarExtraContent"] = tabBarExtraContent
        if tabBarGutter is not None:
            self._props["tabBarGutter"] = tabBarGutter
        if tabBarStyle is not None:
            self._props["tabBarStyle"] = tabBarStyle
        if tabPosition is not None:
            self._props["tabPosition"] = tabPosition 
        if destroyInactiveTabPane is not None:
            self._props["destroyInactiveTabPane"] = destroyInactiveTabPane 
        if type is not None:
            self._props["type"] = type
        if onChange is not None:
            self._props["onChange"] = onChange
        if onEdit is not None:
            self._props["onEdit"] = onEdit
        if onTabClick is not None:
            self._props["onTabClick"] = onTabClick
        if onTabScroll is not None:
            self._props["onTabScroll"] = onTabScroll
