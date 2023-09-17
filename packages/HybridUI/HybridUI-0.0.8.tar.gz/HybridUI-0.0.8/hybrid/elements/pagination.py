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

        self.props["current"] = current
        self.props["defaultCurrent"] = defaultCurrent
        self.props["defaultPageSize"] = defaultPageSize
        self.props["disabled"] = disabled
        self.props["hideOnSinglePage"] = hideOnSinglePage
        self.props["itemRender"] = itemRender
        self.props["pageSize"] = pageSize
        self.props["pageSizeOptions"] = pageSizeOptions
        self.props["responsive"] = responsive
        self.props["showLessItems"] = showLessItems
        self.props["showQuickJumper"] = showQuickJumper
        self.props["showSizeChanger"] = showSizeChanger
        self.props["showTitle"] = showTitle
        self.props["showTotal"] = showTotal
        self.props["simple"] = simple
        self.props["size"] = size
        self.props["total"] = total
        self.props["onChange"] = onChange
        self.props["onShowSizeChange"] = onShowSizeChange
        self.children =content
