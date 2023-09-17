from typing import List, Optional
from ..element import Element


class Rate(Element):

    def __init__(
        self,
        content: List[Element] = None,
        count: int = None,
        defaultValue: float = None,
        allowHalf: bool = False,
        allowClear: bool = True,
        tooltips: List[str] = None,
        character: str = None,
        autoFocus: bool = False,
        disabled: bool = False,
        style: dict = None,
        onBlur = None,
        onChange= None,
        onFocus = None,
        onHoverChange= None,
        onKeyDown= None,
        className = None,
        value = None
    ):
        super().__init__(component='Rate')

        self._props["allowClear"] = allowClear
        self._props["allowHalf"] = allowHalf
        self._props["autoFocus"] = autoFocus
        self._props["character"] = character
        self._props["className"] = className
        self._props["count"] = count
        self._props["defaultValue"] = defaultValue
        self._props["disabled"] = disabled
        self._props["style"] = style
        self._props["tooltips"] = tooltips
        self._props["value"] = value
        self._props["onBlur"] = onBlur
        self._props["onChange"] = onChange
        self._props["onFocus"] = onFocus
        self._props["onHoverChange"] = onHoverChange
        self._props["onKeyDown"] = onKeyDown
        self.children = content
