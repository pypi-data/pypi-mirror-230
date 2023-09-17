from typing import List, Optional, Union, Literal, Callable
from ..element import Element


class Popconfirm(Element):

    def __init__(
        self,
        content: List[Element] = None,
        title: Union[str, Element] = None,
        okText: str = "OK",
        cancelText: str = "Cancel",
        okType: Literal["default", "primary", "dashed", "danger", "link"] = "default",
        icon: Union[str, Element] = None,
        showCancel: bool = True,
        description: Union[str, Element] = None,
        onCancel: Optional[Callable[[], None]] = None,
        onConfirm: Optional[Callable[[], None]] = None,
        onPopupClick: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Popconfirm')

        self.props["cancelButtonProps"] = None
        self.props["cancelText"] = cancelText
        self.props["disabled"] = False
        self.props["icon"] = icon
        self.props["okButtonProps"] = None
        self.props["okText"] = okText
        self.props["okType"] = okType
        self.props["showCancel"] = showCancel
        self.props["title"] = title
        self.props["description"] = description
        self.props["onCancel"] = onCancel
        self.props["onConfirm"] = onConfirm
        self.props["onPopupClick"] = onPopupClick
        self.children = content
