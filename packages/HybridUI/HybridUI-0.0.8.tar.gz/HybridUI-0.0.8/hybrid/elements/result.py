from typing import List, Union, Literal
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Result(Element):

    def __init__(
        self,
        extra: str = None,
        content: List[Element] = None,
        icon: Union[str, Element] = None,
        title: Union[str, Element] = None,
        subTitle: Union[str, Element] = None,
        status: Literal["success", "error", "info", "warning", "404", "403", "500"] = "info"
        # Add more props here if needed
    ):
        super().__init__(component='Result')
        self.children = content
        self.props["extra"] = extra
        self.props["icon"] = icon
        self.props["status"] = status
        self.props["subTitle"] = subTitle
        self.props["title"] = title
