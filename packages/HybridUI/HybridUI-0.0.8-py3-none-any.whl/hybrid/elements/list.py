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
        self.props["bordered"] = bordered
        self.props["dataSource"] = dataSource
        self.props["footer"] = footer
        self.props["grid"] = grid
        self.props["header"] = header
        self.props["itemLayout"] = itemLayout
        self.props["loading"] = loading
        self.props["loadMore"] = loadMore
        self.props["locale"] = locale
        self.props["pagination"] = pagination
        self.props["renderItem"] = renderItem
        self.props["rowKey"] = rowKey
        self.props["size"] = size
        self.props["split"] = split
