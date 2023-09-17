from typing import List, Callable, Union, Optional
from ..element import Element

class ColorPicker(Element):
    """
    ColorPicker:

    allowClear
    arrow
    children
    defaultValue
    disabled
    disabledAlpha
    destroyTooltipOnHide
    format
    open
    presets
    placement
    panelRender
    showText
    size
    trigger
    value
    onChange
    onChangeComplete
    onFormatChange
    onOpenChange
    onClear
    """
    def __init__(
        self,
        content: List[Element] = None,
        title: Optional[str] = None,
        allowClear: bool = None,
        arrow: bool = None,
        children: Element = None,
        defaultValue: str = None,
        disabled: bool = None,
        disabledAlpha: bool = None,
        destroyTooltipOnHide: bool = None,
        format: str = None,
        open: bool = None,
        presets: List[str] = None,
        placement: str = None,
        panelRender: Callable = None,
        showText: bool = None,
        size: str = None,
        trigger: str = None,
        value: str = None,
        onChange: Callable = None,
        onChangeComplete: Callable = None,
        onFormatChange: Callable = None,
        onOpenChange: Callable = None,
        onClear: Callable = None,
    ):
        super().__init__(component='ColorPicker')
        self.children = content

        if title is not None:
            self._props["title"] = title
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if arrow is not None:
            self._props["arrow"] = arrow
        if children is not None:
            self._props["children"] = children
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if disabledAlpha is not None:
            self._props["disabledAlpha"] = disabledAlpha
        if destroyTooltipOnHide is not None:
            self._props["destroyTooltipOnHide"] = destroyTooltipOnHide
        if format is not None:
            self._props["format"] = format
        if open is not None:
            self._props["open"] = open
        if presets is not None:
            self._props["presets"] = presets
        if placement is not None:
            self._props["placement"] = placement
        if panelRender is not None:
            self._props["panelRender"] = panelRender
        if showText is not None:
            self._props["showText"] = showText
        if size is not None:
            self._props["size"] = size
        if trigger is not None:
            self._props["trigger"] = trigger
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            self._props["onChange"] = onChange
        if onChangeComplete is not None:
            self._props["onChangeComplete"] = onChangeComplete
        if onFormatChange is not None:
            self._props["onFormatChange"] = onFormatChange
        if onOpenChange is not None:
            self._props["onOpenChange"] = onOpenChange
        if onClear is not None:
            self._props["onClear"] = onClear
