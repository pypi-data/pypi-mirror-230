from typing import List, Union, Callable, Optional
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Mentions(Element):
    def __init__(
        self,
        content: List[Element] = None,
        value: str = "",
        placeholder: str = "",
        prefix: List[str] = [],
        prefixCls: str = "ant-mentions",
        split: str = " ",
        validateSearch: Callable[[str, List[str]], bool] = None,
        filterOption: Union[bool, Callable[[str, str], bool]] = False,
        autoSize: Union[bool, dict] = False,
        autoFocus: bool = False,
        defaultValue: str = "",
        getPopupContainer = None,
        notFoundContent: Union[str, Element] = "Not Found",
        placement: str = "bottom",
        status: Union[str, Callable[[str, str], str]] = "normal",
        onBlur: Callable[[], None] = None,
        onChange: Callable[[str], None] = None,
        onFocus: Callable[[], None] = None,
        onResize = None,
        onSearch: Callable[[str], None] = None,
        onSelect = None,
        options= [],
    ):
        super().__init__(component='Mentions')
        self.children =content
        self._props["autoSize"] = autoSize
        self._props["autoFocus"] = autoFocus
        self._props["defaultValue"] = defaultValue
        self._props["filterOption"] = filterOption
        self._props["getPopupContainer"] = getPopupContainer
        self._props["notFoundContent"] = notFoundContent
        self._props["placement"] = placement
        self._props["prefix"] = prefix
        self._props["split"] = split
        self._props["status"] = status
        self._props["validateSearch"] = validateSearch
        self._props["value"] = value
        self._props["options"] = options
        self._props["placeholder"] = placeholder
        self._props["prefixCls"] = prefixCls
        self._props["onBlur"] = onBlur
        self._props["onChange"] = onChange
        self._props["onFocus"] = onFocus
        self._props["onResize"] = onResize
        self._props["onSearch"] = onSearch
        self._props["onSelect"] = onSelect
