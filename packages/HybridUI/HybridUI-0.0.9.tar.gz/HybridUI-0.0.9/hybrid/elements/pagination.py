from typing import List, Union,  Optional, Callable, Tuple, Dict, Any, Literal
from ..element import Element



class Pagination(Element):
    def __init__(
        self,
        content: List[Element] = None,
        current: int = 1,
        defaultCurrent: int = 1,
        defaultPageSize: int = 10,
        disabled: bool = False,
        hideOnSinglePage: bool = False,
        itemRender: Callable[[str, Element], Element] = None,
        pageSize: int = 10,
        pageSizeOptions: List[Union[int, str]] = [10, 20, 50, 100],
        responsive: bool = False,
        showLessItems: bool = False,
        showQuickJumper: Union[bool, Dict[str, bool]] = False,
        showSizeChanger: bool = False,
        showTitle: bool = True,
        showTotal: Optional[Callable[[int, Tuple[int, int]], str]] = None,
        simple: bool = False,
        size: Literal["default", "small"] = "default",
        total: int = 0,
        onChange: Optional[Callable[[int, int], None]] = None,
        onShowSizeChange: Optional[Callable[[int, int], None]] = None,
    ):
        super().__init__(component='Pagination')

        self._props["current"] = current
        self._props["defaultCurrent"] = defaultCurrent
        self._props["defaultPageSize"] = defaultPageSize
        self._props["disabled"] = disabled
        self._props["hideOnSinglePage"] = hideOnSinglePage
        self._props["itemRender"] = itemRender
        self._props["pageSize"] = pageSize
        self._props["pageSizeOptions"] = pageSizeOptions
        self._props["responsive"] = responsive
        self._props["showLessItems"] = showLessItems
        self._props["showQuickJumper"] = showQuickJumper
        self._props["showSizeChanger"] = showSizeChanger
        self._props["showTitle"] = showTitle
        self._props["showTotal"] = showTotal
        self._props["simple"] = simple
        self._props["size"] = size
        self._props["total"] = total
        self._props["onChange"] = onChange
        self._props["onShowSizeChange"] = onShowSizeChange
        self.children =content
