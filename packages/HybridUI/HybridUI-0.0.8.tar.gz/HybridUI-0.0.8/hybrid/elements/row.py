from typing import List, Union, Dict, Literal
from ..element import Element


class Row(Element):

    def __init__(
        self,
        content,
        gutter = None,
        justify: Literal["start", "end", "center", "space-around", "space-between"] = None,
        align: Literal["top", "middle", "bottom"] = None,
        wrap: str = None
    ):
        super().__init__(component='UIRow')
        self.children = content
        if gutter is not None:
            self._props["gutter"] = gutter
        if justify is not None:
            self._props["justify"] = justify
        if align is not None:
            self._props["align"] = align
        if wrap is not None:
            self._props["wrap"] = wrap
