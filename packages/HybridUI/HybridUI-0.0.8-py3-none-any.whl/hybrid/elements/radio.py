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
        self.props["autoFocus"] = autoFocus
        self.props["checked"] = checked
        self.props["disabled"] = disabled
        self.props["value"] = value
        self.props["onChange"] = onChange







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
        self.props["buttonStyle"] = buttonStyle
        self.props["defaultValue"] = defaultValue
        self.props["disabled"] = disabled
        self.props["name"] = name
        self.props["options"] = options
        self.props["optionType"] = optionType
        self.props["size"] = size
        self.props["value"] = value
        self.props["onChange"] = onChange
