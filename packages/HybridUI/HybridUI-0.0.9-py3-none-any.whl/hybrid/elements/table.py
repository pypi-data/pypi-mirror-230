from typing import List, Dict
from ..element import Element

class Table(Element):
    """
    Example Usage:
    table = Table(
        columns=[
            {"title": "Name", "dataIndex": "name", "key": "name"},
            {"title": "Age", "dataIndex": "age", "key": "age"},
            {"title": "Address", "dataIndex": "address", "key": "address"},
        ],
        dataSource=[
            {"name": "John", "age": 28, "address": "123 Street"},
            {"name": "Jane", "age": 32, "address": "456 Avenue"},
        ],
        pagination={"pageSize": 10},
        onChange=my_table_change_callback,
    )
    """
    def __init__(
            self, 
            content: List[Element] = None,
            bordered= None,
            columns= None,
            components= None,
            dataSource= None,
            expandable= None,
            footer= None,
            getPopupContainer= None,
            loading= None,
            locale= None,
            pagination= None,
            rowClassName= None,
            rowKey= None,
            rowSelection= None,
            scroll= None,
            showHeader= None,
            showSorterTooltip= None,
            size= None,
            sortDirections= None,
            sticky= None,
            summary= None,
            tableLayout= None,
            fixed= None,
            title= None,
            onChange= None,
            onHeaderRow= None,
            onRow= None

            ):
        super().__init__(component='Table')

        if bordered is not None:
            self._props["bordered"] = bordered
        if columns is not None:
            self._props["columns"] = columns
        if components is not None:
            self._props["components"] = components
        if dataSource is not None:
            self._props["dataSource"] = dataSource
        if expandable is not None:
            self._props["expandable"] = expandable
        if footer is not None:
            self._props["footer"] = footer
        if getPopupContainer is not None:
            self._props["getPopupContainer"] = getPopupContainer
        if loading is not None:
            self._props["loading"] = loading
        if locale is not None:
            self._props["locale"] = locale
        if pagination is not None:
            self._props["pagination"] = pagination
        if rowClassName is not None:
            self._props["rowClassName"] = rowClassName
        if rowKey is not None:
            self._props["rowKey"] = rowKey
        if rowSelection is not None:
            self._props["rowSelection"] = rowSelection
        if scroll is not None:
            self._props["scroll"] = scroll
        if showHeader is not None:
            self._props["showHeader"] = showHeader
        if showSorterTooltip is not None:
            self._props["showSorterTooltip"] = showSorterTooltip
        if size is not None:
            self._props["size"] = size
        if sortDirections is not None:
            self._props["sortDirections"] = sortDirections
        if sticky is not None:
            self._props["sticky"] = sticky
        if summary is not None:
            self._props["summary"] = summary
        if tableLayout  is not None:
            self._props["tableLayout"] = tableLayout
        if fixed is not None:
            self._props["fixed"] = fixed
        if  title is not None:
            self._props["title"] = title
        if onChange is not None:
            self._props["onChange"] = onChange
        if onHeaderRow is not None:
            self._props["onHeaderRow"] = onHeaderRow
        if onRow is not None:
            self._props["onRow"] = onRow
