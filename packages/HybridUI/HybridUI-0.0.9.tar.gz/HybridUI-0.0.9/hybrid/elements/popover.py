from typing import List, Optional, Union, Literal
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Popover(Element):

    def __init__(
        self,
        content: List[Element] = None,
        title: Union[str, Element] = None,
        trigger: Literal["click", "hover", "focus", "contextMenu"] = "hover",
        placement: Literal[
            "topLeft", "top", "topRight", "leftTop", "left", "leftBottom",
            "bottomLeft", "bottom", "bottomRight", "rightTop", "right", "rightBottom"
        ] = "top",
        arrowPointAtCenter: bool = False,
        visible: bool = False,
    ):
        super().__init__(component='Popover')

        self.children = content
        self._props["title"] = title
        self._props["trigger"] = trigger
        self._props["placement"] = placement
        self._props["arrowPointAtCenter"] = arrowPointAtCenter
        self._props["visible"] = visible
