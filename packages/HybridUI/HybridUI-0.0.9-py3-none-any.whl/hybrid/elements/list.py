from typing import List, Optional, Union, Any, Callable, Dict
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class UIList(Element):
    """
    UIList

    Property
    bordered
    dataSource
    footer
    grid
    header
    itemLayout
    loading
    loadMore
    locale
    pagination
    renderItem
    rowKey
    size
    split
    """
    def __init__(
        self,
        content: List[Element] = None,
        dataSource: List[Any] = [],
        renderItem: Optional[Callable[[Any], Element]] = None,
        bordered: bool = False,
        footer: Union[str, Element] = None,
        grid: Optional[Dict[str, Any]] = None,
        header: Union[str, Element] = None,
        itemLayout: Optional[str] = "vertical",
        loading: Union[bool, Dict[str, Any]] = False,
        loadMore: Union[bool, Element] = False,
        locale: dict = None,
        pagination: Union[bool, dict] = None,
        rowKey: Union[str, Callable[[Any], str]] = "key",
        size: str = None,
        split: bool = True,
    ):
        super().__init__(component='UIList')
        self.children = content
        self._props["bordered"] = bordered
        self._props["dataSource"] = dataSource
        self._props["footer"] = footer
        self._props["grid"] = grid
        self._props["header"] = header
        self._props["itemLayout"] = itemLayout
        self._props["loading"] = loading
        self._props["loadMore"] = loadMore
        self._props["locale"] = locale
        self._props["pagination"] = pagination
        self._props["renderItem"] = renderItem
        self._props["rowKey"] = rowKey
        self._props["size"] = size
        self._props["split"] = split
