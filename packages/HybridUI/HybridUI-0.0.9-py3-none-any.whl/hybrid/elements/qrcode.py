from typing import List, Optional, Union, Literal
from ..element import Element


class QRcode(Element):

    def __init__(
        self,
        content: List[Element] = None,
        value: str = None,
        size: int = 128,
        bgColor: str = "#FFFFFF",
        fgColor: str = "#000000",
        level: Literal["L", "M", "Q", "H"] = "M",
        includeMargin: bool = False,
    ):
        super().__init__(component='QRcode')
        self.children= content
        self._props["value"] = value
        self._props["size"] = size
        self._props["bgColor"] = bgColor
        self._props["fgColor"] = fgColor
        self._props["level"] = level
        self._props["includeMargin"] = includeMargin
