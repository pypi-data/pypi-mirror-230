from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Cascder(Element):
    """
    Cascader:

    Property	
    allowClear	
    autoFocus
    bordered	
    changeOnSelect		
    className		
    defaultValue	
    disabled	
    displayRender	
    tagRender	
    popupClassName	
    dropdownRende
    expandIcon	
    expandTrigger	
    fieldNames	
    getPopupContainer	
    loadData		
    maxTagCount	
    maxTagPlaceholder	
    maxTagTextLength	
    notFoundContent		
    open	
    options	
    placeholder	
    placement	
    showSearch	
    size
    status
    style	
    suffixIcon	
    value	
    onChange	
    onDropdownVisibleChange	
    multiple	
    removeIcon	
    showCheckedStrategy		
    searchValue	
    onSearch	
    dropdownMenuColumnStyle	
    loadingIcon	


    """
    def __init__(
        self,
        content: List[Element] = None,
        showSearch: bool = False,
        options: List[dict] = [],
        allowClear = None,	
        autoFocus = None,
        bordered = None,	
        changeOnSelect = None,		
        className = None,		
        defaultValue = None,	
        disabled = None,	
        displayRender = None,	
        tagRender = None,	
        popupClassName = None,	
        dropdownRende = None,
        expandIcon = None,	
        expandTrigger = None,	
        fieldNames = None,	
        getPopupContainer = None,	
        loadData = None,		
        maxTagCount = None,	
        maxTagPlaceholder = None,	
        maxTagTextLength = None,	
        notFoundContent = None,		
        open = None,	
        placeholder = None,	
        placement = None,	
        size = None,
        status = None,
        style = None,	
        suffixIcon = None,	
        value = None,	
        onChange = None,	
        onDropdownVisibleChange = None,	
        multiple = None,	
        removeIcon = None,	
        showCheckedStrategy = None,		
        searchValue = None,	
        onSearch = None,	
        dropdownMenuColumnStyle = None,	
        loadingIcon = None,
    ):
        super().__init__(component='Alert')
        self.children = content
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if bordered is not None:
            self._props["bordered"] = bordered
        if changeOnSelect is not None:
            self._props["changeOnSelect"] = changeOnSelect
        if className is not None:
            self._props["className"] = className
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if displayRender is not None:
            self._props["displayRender"] = displayRender
        if tagRender is not None:
            self._props["tagRender"] = tagRender
        if popupClassName is not None:
            self._props["popupClassName"] = popupClassName
        if dropdownRende is not None:
            self._props["dropdownRende"] = dropdownRende
        if expandIcon is not None:
            self._props["expandIcon"] = expandIcon
        if expandTrigger is not None:
            self._props["expandTrigger"] = expandTrigger
        if fieldNames is not None:
            self._props["fieldNames"] = fieldNames
        if getPopupContainer is not None:
            self._props["getPopupContainer"] = getPopupContainer
        if loadData is not None:
            self._props["loadData"] = loadData
        if maxTagCount is not None:
            self._props["maxTagCount"] = maxTagCount
        if maxTagPlaceholder is not None:
            self._props["maxTagPlaceholder"] = maxTagPlaceholder
        if maxTagTextLength is not None:
            self._props["maxTagTextLength"] = maxTagTextLength
        if notFoundContent is not None:
            self._props["notFoundContent"] = notFoundContent
        if open is not None:
            self._props["open"] = open
        if options is not None:
            self._props["options"] = options
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if placement is not None:
            self._props["placement"] = placement
        if showSearch is not None:
            self._props["showSearch"] = showSearch
        if size is not None:
            self._props["size"] = size
        if status is not None:
            self._props["status"] = status
        if style is not None:
            self._props["style"] = style
        if suffixIcon is not None:
            self._props["suffixIcon"] = suffixIcon
        if value is not None:
            self._props["value"] = value
        if multiple is not None:
            self._props["multiple"] = multiple
        if removeIcon is not None:
            self._props["removeIcon"] = removeIcon
        if showCheckedStrategy is not None:
            self._props["showCheckedStrategy"] = showCheckedStrategy
        if searchValue is not None:
            self._props["searchValue"] = searchValue
        if dropdownMenuColumnStyle is not None:
            self._props["dropdownMenuColumnStyle"] = dropdownMenuColumnStyle
        if loadingIcon is not None:
            self._props["loadingIcon"] = loadingIcon
        if onSearch is not None:
            self._props["onSearch"] = onSearch
        if onDropdownVisibleChange is not None:
            self._props["onDropdownVisibleChange"] = onDropdownVisibleChange
        if onChange is not None:
            self._props["onChange"] = onChange
