from typing import List, Optional, Dict, Callable, Any
from ..element import Element

class Segmented(Element):
    def __init__(
        self,
        content: List[Element] = None,
        value: Any = None,
        options: List[Dict[str, Any]] = [],
        onChange: Optional[Callable[[Any], None]] = None,
    ):
        super().__init__(component='Segmented')
        self.children = content
        self._props["value"] = value
        self._props["options"] = options
        self._props["onChange"] = onChange
