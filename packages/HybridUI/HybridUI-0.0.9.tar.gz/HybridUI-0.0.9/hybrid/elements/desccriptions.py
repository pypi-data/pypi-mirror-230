from typing import List, Union
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Descriptions(Element):
    """
    bordered
    colon
    column
    contentStyle
    extra
    items
    labelStyle
    layout
    size
    title

    DescriptionItem

    Property
    contentStyle
    label
    labelStyle
    span
    """
    def __init__(
        self,
        content: List[Element] = None,
        title: Union[str, Element] = "",
        bordered: bool = False,
        colon: bool = True,
        column: int = 3,
        contentStyle: dict = None,
        extra: Element = None,
        items: List[Element] = None,
        labelStyle: dict = None,
        layout: str = "horizontal",
        size: str = "default",
    ):
        super().__init__(component='Descriptions')
        self.children= content
        self._props["title"] = title
        self._props["bordered"] = bordered
        self._props["colon"] = colon
        self._props["column"] = column
        self._props["contentStyle"] = contentStyle
        self._props["extra"] = extra
        self._props["items"] = items
        self._props["labelStyle"] = labelStyle
        self._props["layout"] = layout
        self._props["size"] = size
