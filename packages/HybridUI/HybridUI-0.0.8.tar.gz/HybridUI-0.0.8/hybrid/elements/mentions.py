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
        self.props["autoSize"] = autoSize
        self.props["autoFocus"] = autoFocus
        self.props["defaultValue"] = defaultValue
        self.props["filterOption"] = filterOption
        self.props["getPopupContainer"] = getPopupContainer
        self.props["notFoundContent"] = notFoundContent
        self.props["placement"] = placement
        self.props["prefix"] = prefix
        self.props["split"] = split
        self.props["status"] = status
        self.props["validateSearch"] = validateSearch
        self.props["value"] = value
        self.props["options"] = options
        self.props["placeholder"] = placeholder
        self.props["prefixCls"] = prefixCls
        self.props["onBlur"] = onBlur
        self.props["onChange"] = onChange
        self.props["onFocus"] = onFocus
        self.props["onResize"] = onResize
        self.props["onSearch"] = onSearch
        self.props["onSelect"] = onSelect
