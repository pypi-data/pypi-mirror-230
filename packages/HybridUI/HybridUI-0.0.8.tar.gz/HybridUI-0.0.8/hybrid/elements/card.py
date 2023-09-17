from typing import Optional
from ..element import Element

class Card(Element):
    """
    Card component.
    """
    def __init__(
        self,
        content = None,
        actions: dict= None,
        activeTabKey: Optional[str] = None,
        bodyStyle: dict = None,
        bordered: bool = None,
        cover = None,
        defaultActiveTabKey: Optional[str] = None,
        extra = None,
        headStyle: dict = None,
        hoverable: bool = None,
        loading: bool = None,
        size: str = None,
        tabBarExtraContent = None,
        tabList: list = None,
        tabProps: dict = None,
        title: Optional[str] = None,
        type: str = None,
        onTabChange: str = None,
    ):
        super().__init__(component='Card')
        self.children = content
        if actions is not None:
            self._props["actions"] = actions
        if activeTabKey is not None:
            self._props["activeTabKey"] = activeTabKey
        if bodyStyle is not None:
            self._props["bodyStyle"] = bodyStyle  
        if bordered is not None:
            self._props["bordered"] = bordered
        if cover is not None:
            self._props["cover"] = cover
        if defaultActiveTabKey is not None:
            self._props["defaultActiveTabKey"] = defaultActiveTabKey
        if extra is not None:
            self._props["extra"] = extra        
        if headStyle is not None:
            self._props["headStyle"] = headStyle       
        if hoverable is not None:
            self._props["hoverable"] = hoverable     
        if loading is not None:
            self._props["loading"] = loading
        if size is not None:
            self._props["size"] = size
        if tabBarExtraContent is not None:
            self._props["tabBarExtraContent"] = tabBarExtraContent      
        if tabList is not None:
            self._props["tabList"] = tabList
        if tabProps is not None:
            self._props["tabProps"] = tabProps
        if title is not None:
            self._props["title"] = title
        if type is not None:
            self._props["type"] = type      
        if onTabChange is not None:
            onTabChange_listner = self.on(onTabChange)
            self._props["onTabChange"] = onTabChange_listner
            

class GridCard(Card):
    """
    GridCard variant of Card.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MetaCard(Card):
    """
    MetaCard variant of Card.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
