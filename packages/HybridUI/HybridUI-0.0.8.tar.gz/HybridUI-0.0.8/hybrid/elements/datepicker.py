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
        self.props["value"] = value
        self.props["onChange"] = onChange
        self.props["allowClear"] = allowClear
        self.props["autoFocus"] = autoFocus
        self.props["bordered"] = bordered
        self.props["className"] = className
        self.props["dateRender"] = dateRender
        self.props["changeOnBlur"] = changeOnBlur
        self.props["cellRender"] = cellRender
        self.props["disabled"] = disabled
        self.props["disabledDate"] = disabledDate
        self.props["popupClassName"] = popupClassName
        self.props["getPopupContainer"] = getPopupContainer
        self.props["inputReadOnly"] = inputReadOnly
        self.props["locale"] = locale
        self.props["mode"] = mode
        self.props["nextIcon"] = nextIcon
        self.props["open"] = open
        self.props["panelRender"] = panelRender
        self.props["picker"] = picker
        self.props["placeholder"] = placeholder
        self.props["placement"] = placement
        self.props["popupStyle"] = popupStyle
        self.props["presets"] = presets
        self.props["prevIcon"] = prevIcon
        self.props["size"] = size
        self.props["status"] = status
        self.props["style"] = style
        self.props["suffixIcon"] = suffixIcon
        self.props["superNextIcon"] = superNextIcon
        self.props["superPrevIcon"] = superPrevIcon
        self.props["onOpenChange"] = onOpenChange
        self.props["onPanelChange"] = onPanelChange
        self.props["defaultPickerValue"] = defaultPickerValue
        self.props["defaultValue"] = defaultValue
        self.props["disabledTime"] = disabledTime
        self.props["format"] = format
        self.props["renderExtraFooter"] = renderExtraFooter
        self.props["showNow"] = showNow
        self.props["showTime"] = showTime
        self.props["showTime.defaultValue"] = showTimeDefaultValue
        self.props["showToday"] = showToday
        self.props["onOk"] = onOk
