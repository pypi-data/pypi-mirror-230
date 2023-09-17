from typing import List
from ..element import Element

class Column(Element):
    """
    Col:
    Property
    flex
    offset
    order
    pull
    push
    span
    xs
    sm
    md
    lg
    xl
    xxl
    """
    def __init__(
        self,
        content= None,
        flex: str = None,
        offset: int =None,
        order: int =None,
        pull: int =None,
        push: int =None,
        span: int = None,
        xs: int = None,
        sm: int = None,
        md: int = None,
        lg: int = None,
        xl: int = None,
        xxl: int = None,
    ):
        super().__init__(component='UIColumn')
        self.children = content

        if flex is not None:
            self._props["flex"] = flex
        if offset is not None:
            self._props["offset"] = offset
        if order is not None:
            self._props["order"] = order
        if pull is not None:
            self._props["pull"] = pull
        if push is not None:
            self._props["push"] = push
        if span is not None:
            self._props["span"] = span
        if xs is not None:
            self._props["xs"] = xs
        if sm is not None:
            self._props["sm"] = sm
        if md is not None:
            self._props["md"] = md
        if lg is not None:
            self._props["lg"] = lg
        if xl is not None:
            self._props["xl"] = xl
        if xxl is not None:
            self._props["xxl"] = xxl
