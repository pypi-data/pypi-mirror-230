from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class AutoComplete(Element):
    """
    AutoComplete:


    allowClear
    autoFocus	
    backfill		
    bordered	
    children 	
    children 
    defaultActiveFirstOption
    defaultOpen	
    defaultValue
    disabled
    popupClassName
    dropdownMatchSelectWiens 
    filterOption	
    notFoundContent		
    open	
    options		
    placeholder	
    status	
    value	
    onBlur	
    onChange	
    onDropdownVisibleChange	
    onFocus		
    onSearch	
    onSelect		
    onClear	

    """
    def __init__(
                self, 
            allowClear= None,
            autoFocus= None,
            backfill= None,		
            bordered= None,	
            children = None,	
            defaultActiveFirstOption= None,
            defaultOpen	= None,
            defaultValue= None,
            disabled= None,
            popupClassName= None,
            dropdownMatchSelectWiens = None,
            filterOption= None,
            notFoundContent= None,
            open= None,
            options= None,
            placeholder= None,
            status= None,
            value= None,
            onBlur= None,
            onChange= None,
            onDropdownVisibleChange= None,
            onFocus= None,
            onSearch= None,
            onSelect= None,
            onClear= None,
            content: List[Element] = None):
        super().__init__(component='Alert')
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if backfill is not None:
            self._props["backfill"] = backfill
        if bordered is not None:
            self._props["bordered"] = bordered
        if children is not None:
            self._props["children"] = children
        if defaultActiveFirstOption is not None:
            self._props["defaultActiveFirstOption"] = defaultActiveFirstOption
        if  defaultOpen is not None:
            self._props["defaultOpen"] = defaultOpen
        if defaultValue  is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName
        if dropdownMatchSelectWiens is not None:
            self._props["dropdownMatchSelectWiens"] = dropdownMatchSelectWiens
        if filterOption is not None:
            self._props["filterOption"] = filterOption
        if notFoundContent is not None:
            self._props["notFoundContent"] = notFoundContent
        if open is not None:
            self._props["open"] = open
        if options is not None:
            self._props["options"] = options
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if status is not None:
            self._props["status"] = status
        if value is not None:
            self._props["value"] = value
        if onBlur is not None:
            self._props["onBlur"] = onBlur
        if onChange is not None:
            onChange_listner = self.on(onChange)
            self._props["onChange"] = onChange_listner
        if onDropdownVisibleChange is not None:
            onDropdownVisibleChange_listner = self.on(onDropdownVisibleChange)                           
            self._props["onDropdownVisibleChange"] = onDropdownVisibleChange_listner
        if onFocus is not None:
            onFocus_listner = self.on(onFocus)
            self._props["onFocus"] = onFocus_listner
        if onSearch  is not None:
            onSearch_listner = self.on(onSearch)
            self._props["onSearch"] = onSearch_listner
        if onSelect is not None:
            onSelect_listner = self.on(onSelect)
            self._props["onSelect"] = onSelect_listner
        if onClear is not None:
            onClear_listner = self.on(onClear)
            self._props["onClear"] = onClear_listner
            self.children= content