from typing import List, Any, Callable, Union
from ..element import Element


class Transfer(Element):
    """
    """

    def __init__(
        self,
        content: List[Element] = None,
        dataSource: List[Any] = None,
        targetKeys: List[Union[str, int]] = None,
        selectedKeys: List[Union[str, int]] = None,
        onChange: Callable = None,
        disabled = None,
        selectionsIcon = None,
        filterOption = None,
        footer = None,
        listStyle = None,
        locale = None,
        oneWay = None,
        operations = None,
        operationStyle = None,
        pagination = None,
        render = None,
        selectAllLabels = None,
        showSearch = None,
        showSelectAll = None,
        status = None,
        titles = None,
        onScroll = None,
        onSearch = None,
        onSelectChange = None,
    ):
        super().__init__(component='Transfer')
        self.children = content
        self._props["dataSource"] = dataSource
        self._props["disabled"] = disabled
        self._props["selectionsIcon"] = selectionsIcon
        self._props["filterOption"] = filterOption
        self._props["footer"] = footer
        self._props["listStyle"] = listStyle
        self._props["locale"] = locale
        self._props["oneWay"] = oneWay
        self._props["operations"] = operations
        self._props["operationStyle"] = operationStyle
        self._props["pagination"] = pagination
        self._props["render"] = render
        self._props["selectAllLabels"] = selectAllLabels
        self._props["selectedKeys"] = selectedKeys
        self._props["showSearch"] = showSearch
        self._props["showSelectAll"] = showSelectAll
        self._props["status"] = status
        self._props["targetKeys"] = targetKeys
        self._props["titles"] = titles
        if not onChange == None:
            self._props["onChange"] = onChange
        if not onScroll == None:
            self._props["onScroll"] = onScroll
        if not onSearch == None:
            self._props["onSearch"] = onSearch
        if not onSelectChange == None:
            self._props["onSelectChange"] = onSelectChange
