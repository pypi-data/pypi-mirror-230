from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Select(Element):

    def __init__(
            self, 
            allowClear= None,		
            autoClearSearchValue= None,  
            autoFocus= None,		
            bordered= None,		
            clearIcon= None,	
            defaultActiveFirstOption= None,	
            defaultOpen= None,	
            defaultValue= None,	
            number= None, 
            LabeledValue= None, 
            disabled= None,	
            popupClassName= None,	
            popupMatchSelectWidth= None,		
            dropdownRender= None,	
            dropdownStyle= None,		
            fieldNames= None,  
            filterOption= None,	
            filterSort= None,		
            getPopupContainer= None,		
            labelInValue= None,	
            listHeight= None,	
            loading= None,		
            maxTagCount= None,	
            maxTagPlaceholder= None,		
            maxTagTextLength= None,	
            menuItemSelectedIcon= None,	
            mode= None,	
            notFoundContent= None,	
            open= None,	
            optionFilterProp= None,
            optionLabelProp= None,		
            options= None,	
            placeholder= None,	
            status= None,	
            suffixIcon= None,	
            tagRender= None,	
            tokenSeparators= None,	
            value= None,	
            virtual= None,	
            placement= None,
            removeIcon= None,
            searchValue= None,
            showSearch= None,
            size= None,
            onBlur= None,	
            onChange= None,
            onClear= None,	
            onDeselect= None,	
            onDropdownVisibleChange= None,	
            onFocus= None,	
            onInputKeyDown= None,	
            onMouseEnter= None,		
            onMouseLeave= None,	
            onPopupScroll= None,	
            onSearch= None,		
            onSelect= None,
            ):
        super().__init__(component='Select')
        self.children =[]
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoClearSearchValue is not None:
            self._props["autoClearSearchValue"] = autoClearSearchValue
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if bordered is not None:
            self._props["bordered"] = bordered
        if clearIcon is not None:
            self._props["clearIcon"] = clearIcon
        if defaultActiveFirstOption is not None:
            self._props["defaultActiveFirstOption"] = defaultActiveFirstOption
        if defaultOpen is not None:
            self._props["defaultOpen"] = defaultOpen
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName
        if popupMatchSelectWidth is not None:
            self._props["popupMatchSelectWidth"] = popupMatchSelectWidth
        if dropdownRender is not None:
            self._props["dropdownRender"] = dropdownRender
        if dropdownStyle is not None:
            self._props["dropdownStyle"] = dropdownStyle
        if fieldNames is not None:
            self._props["fieldNames"] = fieldNames
        if filterOption is not None:
            self._props["filterOption"] = filterOption
        if filterSort is not None:
            self._props["filterSort"] = filterSort
        if getPopupContainer is not None:
            self._props["getPopupContainer"] = getPopupContainer
        if labelInValue is not None:
            self._props["labelInValue"] = labelInValue
        if listHeight is not None:
            self._props["listHeight"] = listHeight
        if loading is not None:
            self._props["loading"] = loading
        if maxTagCount is not None:
            self._props["maxTagCount"] = maxTagCount
        if maxTagPlaceholder is not None:
            self._props["maxTagPlaceholder"] = maxTagPlaceholder
        if maxTagTextLength is not None:
            self._props["maxTagTextLength"] = maxTagTextLength
        if  menuItemSelectedIcon is not None:
            self._props["menuItemSelectedIcon"] = menuItemSelectedIcon
        if mode is not None:
            self._props["mode"] = mode
        if notFoundContent is not None:
            self._props["notFoundContent"] = notFoundContent
        if open is not None:
            self._props["open"] = open
        if optionFilterProp is not None:
            self._props["optionFilterProp"] = optionFilterProp
        if optionLabelProp is not None:
            self._props["optionLabelProp"] = optionLabelProp
        if options is not None:
            self._props["options"] = options
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if placement is not None:
            self._props["placement"] = placement
        if removeIcon is not None:
            self._props["removeIcon"] = removeIcon
        if searchValue is not None:
            self._props["searchValue"] = searchValue
        if showSearch  is not None:
            self._props["showSearch"] = showSearch
        if size is not None:
            self._props["size"] = size
        if status is not None:
            self._props["status"] =status
        if suffixIcon  is not None:
            self._props["suffixIcon"] =suffixIcon	
        if tagRender is not None:
            self._props["tagRender"] =tagRender	
        if tokenSeparators is not None:
            self._props["tokenSeparators"] =tokenSeparators	
        if value  is not None:
            self._props["value"] =value	
        if number is not None:
            self._props["number"] =number 
        if LabeledValue is not None:
            self._props["LabeledValue"] =LabeledValue 
        if virtual is not None:
            self._props["virtual"] =virtual	
        if onBlur is not None:
            self._props["onBlur"] =onBlur	
        if onChange is not None:
            self._props["onChange"] =onChange
        if onClear is not None:
            self._props["onClear"] =onClear	
        if onDeselect is not None:
            self._props["onDeselect"] =onDeselect	
        if onDropdownVisibleChange is not None:
            self._props["onDropdownVisibleChange"] =onDropdownVisibleChange	
        if onFocus  is not None:
            self._props["onFocus"] =onFocus	
        if onInputKeyDown is not None:
            self._props["onInputKeyDown"] =onInputKeyDown	
        if onMouseEnter  is not None:
            self._props["onMouseEnter"] =onMouseEnter		
        if onMouseLeave is not None:
            self._props["onMouseLeave"] =onMouseLeave	
        if onPopupScroll  is not None:
            self._props["onPopupScroll"] =onPopupScroll	
        if onSearch is not None:
            self._props["onSearch"] =onSearch		
        if onSelect is not None:
            self._props["onSelect"] =onSelect	


