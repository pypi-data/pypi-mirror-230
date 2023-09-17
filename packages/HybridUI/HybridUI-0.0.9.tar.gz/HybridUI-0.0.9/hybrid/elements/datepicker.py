from typing import List, Any, Callable, Optional
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class DatePicker(Element):
    """
    allowClear
    autoFocus
    bordered
    className
    dateRender
    changeOnBlur
    cellRender
    disabled
    disabledDate
    popupClassName
    getPopupContainer
    inputReadOnly
    locale
    mode
    nextIcon
    open
    panelRender
    picker
    placeholder
    placement
    popupStyle
    presets
    prevIcon
    size
    status
    style
    suffixIcon
    superNextIcon
    superPrevIcon
    onOpenChange
    onPanelChange
    defaultPickerValue
    defaultValue
    disabledTime
    format
    renderExtraFooter
    showNow
    showTime
    showTime.defaultValue
    showToday
    value
    onChange
    onOk
    """
    def __init__(
        self,
        content: List[Element] = None,
        value: Any = None,
        onChange: Optional[Callable[[Any], None]] = None,
        allowClear: bool = True,
        autoFocus: bool = False,
        bordered: bool = True,
        className: str = None,
        dateRender: Callable = None,
        changeOnBlur: bool = False,
        cellRender: Callable = None,
        disabled: bool = False,
        disabledDate: Callable = None,
        popupClassName: str = None,
        getPopupContainer: Callable = None,
        inputReadOnly: bool = False,
        locale: Any = None,
        mode: str = "date",
        nextIcon: Any = None,
        open: bool = False,
        panelRender: Callable = None,
        picker: str = "date",
        placeholder: str = None,
        placement: str = "bottomLeft",
        popupStyle: dict = None,
        presets: List[Element] = None,
        prevIcon: Any = None,
        size: str = "default",
        status: str = None,
        style: dict = None,
        suffixIcon: Any = None,
        superNextIcon: Any = None,
        superPrevIcon: Any = None,
        onOpenChange: Callable = None,
        onPanelChange: Callable = None,
        defaultPickerValue: Any = None,
        defaultValue: Any = None,
        disabledTime: Callable = None,
        format: str = "YYYY-MM-DD",
        renderExtraFooter: Callable = None,
        showNow: bool = False,
        showTime: bool = False,
        showTimeDefaultValue: Any = None,
        showToday: bool = True,
        onOk: Callable = None,
    ):
        super().__init__(component='DatePicker')
        self.children= content
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            self._props["onChange"] = onChange
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if bordered is not None:
            self._props["bordered"] = bordered
        if className is not None:
            self._props["className"] = className
        if dateRender is not None:
            self._props["dateRender"] = dateRender
        if changeOnBlur is not None:
            self._props["changeOnBlur"] = changeOnBlur
        if cellRender is not None:
            self._props["cellRender"] = cellRender
        if disabled is not None:
            self._props["disabled"] = disabled
        if disabledDate is not None:
            self._props["disabledDate"] = disabledDate
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName
        if getPopupContainer is not None:
            self._props["getPopupContainer"] = getPopupContainer
        if inputReadOnly is not None:
            self._props["inputReadOnly"] = inputReadOnly
        if locale is not None:
            self._props["locale"] = locale
        if mode is not None:
            self._props["mode"] = mode
        if nextIcon is not None:
            self._props["nextIcon"] = nextIcon
        if open is not None:
            self._props["open"] = open
        if panelRender is not None:
            self._props["panelRender"] = panelRender
        if picker is not None:
            self._props["picker"] = picker
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if placement is not None:
            self._props["placement"] = placement
        if popupStyle is not None:
            self._props["popupStyle"] = popupStyle
        if presets is not None:
            self._props["presets"] = presets
        if prevIcon is not None:
            self._props["prevIcon"] = prevIcon
        if size is not None:
            self._props["size"] = size
        if status is not None:
            self._props["status"] = status
        if style is not None:
            self._props["style"] = style
        if suffixIcon is not None:
            self._props["suffixIcon"] = suffixIcon
        if superNextIcon is not None:
            self._props["superNextIcon"] = superNextIcon
        if superPrevIcon is not None:
            self._props["superPrevIcon"] = superPrevIcon
        if onOpenChange is not None:
            self._props["onOpenChange"] = onOpenChange
        if onPanelChange is not None:
            self._props["onPanelChange"] = onPanelChange
        if defaultPickerValue is not None:
            self._props["defaultPickerValue"] = defaultPickerValue
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabledTime is not None:
            self._props["disabledTime"] = disabledTime
        if format is not None:
            self._props["format"] = format
        if renderExtraFooter is not None:
            self._props["renderExtraFooter"] = renderExtraFooter
        if showNow is not None:
            self._props["showNow"] = showNow
        if showTime is not None:
            self._props["showTime"] = showTime
        if showTimeDefaultValue is not None:
            self._props["showTimedefaultValue"] = showTimeDefaultValue
        if showToday is not None:
            self._props["showToday"] = showToday
        if onOk is not None:
            self._props["onOk"] = onOk
