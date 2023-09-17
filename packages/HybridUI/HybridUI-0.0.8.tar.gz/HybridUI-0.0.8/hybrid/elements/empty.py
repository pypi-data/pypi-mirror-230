from typing import List, Union
from ..element import Element

class Empty(Element):
    """
    Empty component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        image: str = "",
        description: Union[str, Element] = "",
    
    ):
        super().__init__(component='Empty')
        self.props["description"] = description
        self.props["image"] = image
        self.props["imageStyle"] = None
        self.children = content
