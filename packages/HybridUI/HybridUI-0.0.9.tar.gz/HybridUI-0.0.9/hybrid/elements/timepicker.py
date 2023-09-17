from typing import List, Dict
from ..element import Element

class TimePicker(Element):
    """

    Example Usage:
    time_picker = TimePicker(
        allowClear=True,
        autoFocus=False,
        bordered=True,
        # ... (other properties)
    )
    """
    def __init__(
            self, 
            allowClear= None, 
            autoFocus= None, 
            bordered= None, 
            cellRender= None, 
            changeOnBlur= None, 
            className= None, 
            clearIcon= None, 
            clearText= None, 
            defaultValue= None, 
            disabled= None,
            disabledTime= None, 
            format= None, 
            getPopupContainer= None, 
            hideDisabledOptions= None, 
            hourStep= None, 
            inputReadOnly= None, 
            minuteStep= None, 
            open= None, 
            placeholder= None, 
            placement= None, 
            popupClassName= None,
            popupStyle= None, 
            renderExtraFooter= None, 
            secondStep= None, 
            showNow= None, 
            size= None, 
            suffixIcon= None, 
            use12Hours= None, 
            value= None, 
            onChange= None, 
            onOpenChange= None, 
            onSelect= None,
            status= None
            ):
        super().__init__(component='TimePicker')
        self.children =[]
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if bordered is not None:
            self._props["bordered"] = bordered
        if cellRender is not None:
            self._props["cellRender"] = cellRender
        if changeOnBlur is not None:
            self._props["changeOnBlur"] = changeOnBlur
        if className is not None:
            self._props["className"] = className
        if clearIcon is not None:
            self._props["clearIcon"] = clearIcon
        if clearText is not None:
            self._props["clearText"] = clearText 
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue 
        if disabled is not None:
            self._props["disabled"] = disabled 
        if disabledTime is not None:
            self._props["disabledTime"] = disabledTime
        if format is not None:
            self._props["format"] = format
        if getPopupContainer is not None:
            self._props["getPopupContainer"] = getPopupContainer
        if hideDisabledOptions is not None:
            self._props["hideDisabledOptions"] = hideDisabledOptions
        if hourStep is not None:
            self._props["hourStep"] = hourStep
        if inputReadOnly is not None:
            self._props["inputReadOnly"] = inputReadOnly
        if minuteStep is not None:
            self._props["minuteStep"] = minuteStep 
        if open is not None:
            self._props["open"] = open
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if placement is not None:
            self._props["placement"] = placement
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName
        if popupStyle is not None:
            self._props["popupStyle"] = popupStyle
        if renderExtraFooter is not None:
            self._props["renderExtraFooter"] = renderExtraFooter 
        if secondStep is not None:
            self._props["secondStep"] = secondStep
        if showNow is not None:
            self._props["showNow"] = showNow
        if size is not None:
            self._props["size"] = size 
        if status is not None:
            self._props["status"] = status
        if suffixIcon is not None:
            self._props["suffixIcon"] = suffixIcon
        if use12Hours is not None:
            self._props["use12Hours"] = use12Hours
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            self._props["onChange"] = onChange
        if onOpenChange is not None:
            self._props["onOpenChange"] = onOpenChange
        if onSelect is not None:
            self._props["onSelect"] = onSelect


class RangePicker(Element):
    def __init__(self, order= None, disabledTime= None)-> None:
        super().__init__(component='RangePicker')
        self.children =[]
        if disabledTime is not None:
            self._props["disabledTime"] = disabledTime
        if order is not None:
            self._props["order"] = order

