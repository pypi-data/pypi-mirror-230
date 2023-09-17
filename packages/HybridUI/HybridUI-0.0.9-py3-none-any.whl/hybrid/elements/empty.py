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
        self._props["description"] = description
        self._props["image"] = image
        self._props["imageStyle"] = None
        self.children = content
