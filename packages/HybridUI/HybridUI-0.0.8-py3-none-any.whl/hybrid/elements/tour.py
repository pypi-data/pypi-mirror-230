from typing import List, Any, Dict
from ..element import Element



class Tour(Element):
    """
            self.props["TourStep"] = {
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
        self.props["steps"] = steps
        self.props["initialStep"] = initialStep
        self.props["arrow"] = arrow
        self.props["placement"] = placement
        if not onClose == None:
            self.props["onClose"] = onClose
        self.props["mask"] = mask
        self.props["type"] = type
        self.props["open"] = open
        if not onChange == None:
            self.props["onChange"] = onChange
        self.props["current"] = current
        self.props["scrollIntoViewOptions"] = scrollIntoViewOptions
        self.props["indicatorsRender"] = indicatorsRender
        self.props["zIndex"] = zIndex

