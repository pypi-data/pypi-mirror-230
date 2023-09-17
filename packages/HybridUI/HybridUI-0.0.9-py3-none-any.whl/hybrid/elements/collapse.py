from typing import List, Callable, Union
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Collapse(Element):
    
    """
    accordion	
    activeKey	
    number
    bordered	
    collapsible		
    defaultActiveKey	
    number
    destroyInactivePanel		
    expandIcon	
    expandIconPosition	
    ghost 
    size	
    onChange	
    items		
        
    """
    def __init__(
        self,
        content: List[Element] = None,
        accordion: bool = None,
        activeKey: Union[str, List[str]] = None,
        bordered: bool = None,
        collapsible: bool = None,
        defaultActiveKey: Union[str, List[str]] = None,
        destroyInactivePanel: bool = None,
        expandIcon: Element = None,
        expandIconPosition: str = None,
        ghost: bool = None,
        size: str = None,
        onChange: Callable = None,
        items: List[Element] = None,
    ):
        super().__init__(component='Collapse')

        if accordion is not None:
            self._props["accordion"] = accordion
        if activeKey is not None:
            self._props["activeKey"] = activeKey
        if bordered is not None:
            self._props["bordered"] = bordered
        if collapsible is not None:
            self._props["collapsible"] = collapsible
        if defaultActiveKey is not None:
            self._props["defaultActiveKey"] = defaultActiveKey
        if destroyInactivePanel is not None:
            self._props["destroyInactivePanel"] = destroyInactivePanel
        if expandIcon is not None:
            self._props["expandIcon"] = expandIcon
        if expandIconPosition is not None:
            self._props["expandIconPosition"] = expandIconPosition
        if ghost is not None:
            self._props["ghost"] = ghost
        if size is not None:
            self._props["size"] = size
        if onChange is not None:
            self._props["onChange"] = onChange
        if items is not None:
            self._props["items"] = items
        self.children =content




class CollapsePanel(Element):
    """
    Collapse.Panel

    Property
    collapsible
    extra
    forceRender
    header
    key
    showArrow
    """
    def __init__(
        self,
        content,
        collapsible: bool = True,
        extra: Element = None,
        forceRender: bool = False,
        header: Union[str, Element] = None,
        key: str = None,
        showArrow: bool = True,
    ):
        super().__init__('CollapsePanel', content)
        if collapsible is not None:
            self._props["collapsible"] = collapsible
        if extra is not None:
            self._props["extra"] = extra
        if forceRender is not None:
            self._props["forceRender"] = forceRender
        if header is not None:
            self._props["header"] = header
        if key is not None:
            self._props["key"] = key
        if showArrow is not None:
            self._props["showArrow"] = showArrow
