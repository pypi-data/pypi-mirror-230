from typing import Any, Dict, List, Optional, Callable, Union
from ..element import Element



class Input(Element):
    def __init__(
        self, 
        addonAfter: str = None, 
        addonBefore: str = None, 
        allowClear: bool = None, 
        bordered: bool = None, 
        classNames: str = None, 
        defaultValue: str = None, 
        disabled: bool = None, 
        id: str = None, 
        maxLength: str = None, 
        showCount: bool = None, 
        status: str = None,
        styles: str = None, 
        prefix: str = None, 
        size: str = None, 
        suffix: str = None, 
        type: str = None, 
        value: str = None, 
        onChange: Callable[[str], None] = None, 
        onPressEnter: Callable[[], None] = None, 
        placeholder: str = None
    ) -> None:
        super().__init__(component = 'Input' )
        self.children = []
        if addonAfter is not None:
            self._props['addonAfter'] = addonAfter
        if placeholder is not None:
            self._props['placeholder'] = placeholder
            
        if addonBefore is not None:
            self._props['addonBefore'] = addonBefore
        if allowClear is not None:
            self._props['allowClear'] = allowClear
        if bordered is not None:
            self._props['bordered'] = bordered
        if classNames is not None:
            self._props['classNames'] = classNames
        if defaultValue is not None:
            self._props['defaultValue'] = defaultValue
        if disabled is not None:
            self._props['disabled'] = disabled
        if id is not None:
            self._props['id'] = id
        if maxLength is not None:
            self._props['maxLength'] = maxLength
        if showCount is not None:
            self._props['showCount'] = showCount
        if status is not None:
            self._props['status'] = status
        if styles is not None:
            self._props['styles'] = styles
        if prefix is not None:
            self._props['prefix'] = prefix
        if size is not None:
            self._props['size'] = size
        if suffix is not None:
            self._props['suffix'] = suffix
        if type is not None:
            self._props['type'] = type
        if value is not None:
            self._props['value'] = value
        if onChange is not None:
            regester_handler = self.on(onChange)
            self._props['onChange'] = regester_handler
        if onPressEnter is not None:
            regester_handler1 = self.on(onPressEnter)
            self._props['onPressEnter'] = regester_handler1











class TextArea(Element):
    def __init__(
        self,
        allowClear: Union[bool, dict] = False,
        autoSize: Union[bool, dict] = False,
        bordered: bool = True,
        classNames: dict = None,
        defaultValue: str = None,
        maxLength: int = None,
        showCount: Union[bool, dict] = False,
        styles: dict = None,
        value: str = None,
        onPressEnter: Callable[[str], None] = None,
        onResize: Callable[[dict], None] = None,	
    ) -> None:
        super().__init__(component='TextAreaInput')
        self.children = []
        if allowClear is not None:
            self._props["allowClear"] = allowClear
        if autoSize is not None:
            self._props["autoSize"] = autoSize
        if bordered is not None:
            self._props["bordered"] = bordered
        if classNames is not None:
            self._props["classNames"] = classNames
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if maxLength is not None:
            self._props["maxLength"] = maxLength
        if showCount is not None:
            self._props["showCount"] = showCount
        if styles is not None:
            self._props["styles"] = styles
        if value is not None:
            self._props["value"] = value
        if onPressEnter is not None:
            onPressEnter_listner = self.on(onPressEnter)
            self._props["onPressEnter"] = onPressEnter_listner
        if onResize is not None:
            onResize_listner = self.on(onResize)
            self._props["onResize"] = onResize_listner





class InputSearch(Element):
    def __init__(
        self,
        enterButton: Union[bool, Callable[[str, dict], None]] = False,
        loading: bool = False,
        onSearch: Callable[[str, dict], None] = None
    ) -> None:
        super().__init__(component='SearchInput')
        self.children = []
        if enterButton is not None:
            self._props["enterButton"] = enterButton
        if loading is not None:
            self._props["loading"] = loading
        if onSearch is not None:
            onSearch_listner = self.on(onSearch)
            self._props["onSearch"] = onSearch_listner












class Password(Element):
    def __init__(self, 
    iconRender=None,
    visibilityToggle=None,	
    visible=None,
    onVisibleChange=None,
    Name=None,
    blur=None,
    focus=None,	
    prefix=None,
    suffix=None,
    count=None,
    onChange=None
    ):
        super().__init__(component='PasswordInput')
        self.children = []
        if iconRender is not None:
            self._props["iconRender"]=iconRender
        if visibilityToggle is not None:
            listner = self.on(visibilityToggle)
            self._props["visibilityToggle"]=listner
        if visible is not None:
            self._props["visible"]=visible
        if Name is not None:
            self._props["Name"]=Name
        if prefix is not None:
            self._props["prefix"]=prefix
        if suffix is not None:
            self._props["suffix"]=suffix
        if count is not None:
            self._props["count"]=count
        if onVisibleChange is not None:
            listner = self.on(onVisibleChange)
            self._props["onVisibleChange"]=listner
        if blur  is not None:
            self._props["blur"]=blur
        if focus is not None:
            self._props["focus"]=focus
        if onChange is not None:
            listner = self.on(onChange)
            self._props["onChange"]=listner
     





class INputNummber(Element):
    def __init__(
        self,
        addonAfter: str = None,
        addonBefore: str = None,
        autoFocus: bool = False,
        bordered: bool = True,
        controls: bool = False,
        decimalSeparator: str = None,
        defaultValue: Union[int, float] = None,
        disabled: bool = False,
        formatter: Callable[[Union[int, float]], str] = None,
        keyboard: bool = True,
        max: Union[int, float] = None,
        min: Union[int, float] = None,
        parser: Callable[[str], Union[int, float]] = None,
        precision: int = None,
        readOnly: bool = False,
        status: str = None,
        prefix: Union[str, Element] = None,
        size: str = None,
        step: Union[int, float] = None,
        stringMode: bool = False,
        value: Union[int, float] = None,
        onChange: Callable[[Union[int, float]], None] = None,
        onPressEnter: Callable[[str], None] = None,
        onStep: Callable[[str], None] = None
    ):
        super().__init__(component='InputNummber')
        self.children = []
        if addonAfter is not None:
            self._props["addonAfter"] = addonAfter
        if addonBefore is not None:
            self._props["addonBefore"] = addonBefore
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if bordered is not None:
            self._props["bordered"] = bordered
        if controls is not None:
            self._props["controls"] = controls
        if decimalSeparator is not None:
            self._props["decimalSeparator"] = decimalSeparator
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if formatter is not None:
            self._props["formatter"] = formatter
        if keyboard is not None:
            self._props["keyboard"] = keyboard
        if max is not None:
            self._props["max"] = max
        if min is not None:
            self._props["min"] = min
        if parser is not None:
            self._props["parser"] = parser
        if precision is not None:
            self._props["precision"] = precision
        if readOnly is not None:
            self._props["readOnly"] = readOnly
        if status is not None:
            self._props["status"] = status
        if prefix is not None:
            self._props["prefix"] = prefix
        if size is not None:
            self._props["size"] = size
        if step is not None:
            self._props["step"] = step
        if stringMode is not None:
            self._props["stringMode"] = stringMode
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            onChange_listner = self.on(onChange)
            self._props["onChange"] = onChange_listner
        if onPressEnter is not None:
            onPressEnter_listner = self.on(onPressEnter)
            self._props["onPressEnter"] = onPressEnter_listner
        if onStep is not None:
            onStep_listner = self.on(onStep)
            self._props["onStep"] = onStep_listner
