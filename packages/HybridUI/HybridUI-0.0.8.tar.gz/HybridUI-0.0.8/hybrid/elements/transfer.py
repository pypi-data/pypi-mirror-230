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
        self.props["dataSource"] = dataSource
        self.props["disabled"] = disabled
        self.props["selectionsIcon"] = selectionsIcon
        self.props["filterOption"] = filterOption
        self.props["footer"] = footer
        self.props["listStyle"] = listStyle
        self.props["locale"] = locale
        self.props["oneWay"] = oneWay
        self.props["operations"] = operations
        self.props["operationStyle"] = operationStyle
        self.props["pagination"] = pagination
        self.props["render"] = render
        self.props["selectAllLabels"] = selectAllLabels
        self.props["selectedKeys"] = selectedKeys
        self.props["showSearch"] = showSearch
        self.props["showSelectAll"] = showSelectAll
        self.props["status"] = status
        self.props["targetKeys"] = targetKeys
        self.props["titles"] = titles
        if not onChange == None:
            self.props["onChange"] = onChange
        if not onScroll == None:
            self.props["onScroll"] = onScroll
        if not onSearch == None:
            self.props["onSearch"] = onSearch
        if not onSelectChange == None:
            self.props["onSelectChange"] = onSelectChange
