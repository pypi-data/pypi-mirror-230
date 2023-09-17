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
        self.props["title"] = title
        self.props["bordered"] = bordered
        self.props["colon"] = colon
        self.props["column"] = column
        self.props["contentStyle"] = contentStyle
        self.props["extra"] = extra
        self.props["items"] = items
        self.props["labelStyle"] = labelStyle
        self.props["layout"] = layout
        self.props["size"] = size
