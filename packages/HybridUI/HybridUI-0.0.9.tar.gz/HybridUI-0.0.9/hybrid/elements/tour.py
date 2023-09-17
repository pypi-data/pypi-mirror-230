from typing import List, Any, Dict
from ..element import Element



class Tour(Element):
    """
            self._props["TourStep"] = {
            "target": None,
            "arrow": None,
            "cover": None,
            "title": None,
            "description": None,
            "placement": None,
            "onClose": None,
            "mask": None,
            "type": None,
            "nextButtonProps": None,
            "prevButtonProps": None,
            "scrollIntoViewOptions": None,
        }


    """

    def __init__(
        self,
        content: List[Element] = None,
        steps: List[Dict[str, Any]] = None,
        initialStep: int = 0,
        arrow = None,
        placement = None,
        onClose = None,
        mask = None,
        onChange = None,
        current = None,
        scrollIntoViewOptions = None,
        indicatorsRender = None,
        zIndex = None,
        open= None,
        type= None
    ):
        super().__init__(component='Tour')
        self.children=content
        self._props["steps"] = steps
        self._props["initialStep"] = initialStep
        self._props["arrow"] = arrow
        self._props["placement"] = placement
        if not onClose == None:
            self._props["onClose"] = onClose
        self._props["mask"] = mask
        self._props["type"] = type
        self._props["open"] = open
        if not onChange == None:
            self._props["onChange"] = onChange
        self._props["current"] = current
        self._props["scrollIntoViewOptions"] = scrollIntoViewOptions
        self._props["indicatorsRender"] = indicatorsRender
        self._props["zIndex"] = zIndex

