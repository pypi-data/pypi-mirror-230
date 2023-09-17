from typing import List, Optional
from ..element import Element

class Carousel(Element):
    """
    Carousel component.
    """
    def __init__(
        self,
        content= None,
        autoplay: bool = None,
        dotPosition: str = None,
        dots: bool = None,
        waitForAnimate: bool = None,
        easing: str = None,
        effect: str = None,
        afterChange: str = None,
        beforeChange: str = None,
    ):
        super().__init__('Carousel')
        self.content = content
        if autoplay is not None:
            self._props["autoplay"] = autoplay
        if dotPosition is not None:
            self._props["dotPosition"] = dotPosition
        if dots is not None:
            self._props["dots"] = dots
        if waitForAnimate is not None:
            self._props["waitForAnimate"] = waitForAnimate
        if easing is not None:
            self._props["easing"] = easing
        if effect is not None:
            self._props["effect"] = effect
        if afterChange is not None:
            self._props["afterChange"] = afterChange
        if beforeChange  is not None:
            self._props["beforeChange"] = beforeChange
        
