from typing import List, Optional, Union, Callable, Any, Literal
from ..element import Element


# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert
class ButtonRadio(Element):

    def __init__(
        self,
        content: List[Element] = None,
        value: Any = None,
        checked: bool = False,
        disabled: bool = False,
        onChange: Optional[Callable[[Any], None]] = None,
        autoFocus = None
    ):
        super().__init__(component='ButtonRadio')
        self.children = content
        self._props["autoFocus"] = autoFocus
        self._props["checked"] = checked
        self._props["disabled"] = disabled
        self._props["value"] = value
        self._props["onChange"] = onChange







class RadioGroup(Element):

    def __init__(
        self,
        content: List[Element] = None,
        value: Any = None,
        defaultValue: Any = None,
        disabled: bool = False,
        name: str = None,
        options: List[dict] = None,
        optionType: Literal["button", "radio"] = "radio",
        size: Literal["small", "middle", "large"] = "middle",
        onChange: Optional[Callable[[Any], None]] = None,
        buttonStyle = None,
    ):
        super().__init__(component='RadioGroup')
        self.children = content
        self._props["buttonStyle"] = buttonStyle
        self._props["defaultValue"] = defaultValue
        self._props["disabled"] = disabled
        self._props["name"] = name
        self._props["options"] = options
        self._props["optionType"] = optionType
        self._props["size"] = size
        self._props["value"] = value
        self._props["onChange"] = onChange
