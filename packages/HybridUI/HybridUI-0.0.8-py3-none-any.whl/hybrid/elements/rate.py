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

        self.props["allowClear"] = allowClear
        self.props["allowHalf"] = allowHalf
        self.props["autoFocus"] = autoFocus
        self.props["character"] = character
        self.props["className"] = className
        self.props["count"] = count
        self.props["defaultValue"] = defaultValue
        self.props["disabled"] = disabled
        self.props["style"] = style
        self.props["tooltips"] = tooltips
        self.props["value"] = value
        self.props["onBlur"] = onBlur
        self.props["onChange"] = onChange
        self.props["onFocus"] = onFocus
        self.props["onHoverChange"] = onHoverChange
        self.props["onKeyDown"] = onKeyDown
        self.children = content
