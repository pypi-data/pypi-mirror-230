from typing import List, Callable
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Checkbox(Element):
    """
    Checkbox:
    autoFocus	
    checked	
    defaultChecked	
    disabled	
    indeterminate		
    onChange
    """
    def __init__(
        self,
        content: List[Element] = None,
        autoFocus = None,
        checked: bool = None,
        defaultChecked=None,
        disabled: bool = None,
        indeterminate=None,
        onChange: Callable = None,
    ):
        super().__init__(component='Checkbox')
        self.children = [content]
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if checked is not None:
            self._props["checked"] = checked
        if defaultChecked is not None:
            self._props["defaultChecked"] = defaultChecked
        if disabled is not None:
            self._props["disabled"] = disabled
        if indeterminate is not None:
            self._props["indeterminate"] = indeterminate
        if onChange is not None:
            handel_onchange = self.on(onChange)
            self._props["onChange"] = handel_onchange
        







class CheckboxGroup(Element):
    """
    Checkbox(Group):

    Property	
    defaultValue	
    disabled	
    name	
    options	
    value		
    onChange	

    """
    def __init__(
        self,
        content: List[Element] = None,
        name = None,
        options: bool = False,
        defaultValue=None,
        disabled: bool = False,
        value=None,
        onChange: Callable = None,
    ):
        super().__init__(component='CheckboxGroup')
        self.children = content
        if name is not None:
            self._props["name"] = name
        if options is not None:
            self._props["options"] = options
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            self._props["onChange"] = onChange
        