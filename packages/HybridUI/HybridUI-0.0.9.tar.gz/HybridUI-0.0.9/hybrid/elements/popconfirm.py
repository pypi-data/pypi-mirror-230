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

        self._props["cancelButtonProps"] = None
        self._props["cancelText"] = cancelText
        self._props["disabled"] = False
        self._props["icon"] = icon
        self._props["okButtonProps"] = None
        self._props["okText"] = okText
        self._props["okType"] = okType
        self._props["showCancel"] = showCancel
        self._props["title"] = title
        self._props["description"] = description
        self._props["onCancel"] = onCancel
        self._props["onConfirm"] = onConfirm
        self._props["onPopupClick"] = onPopupClick
        self.children = content
