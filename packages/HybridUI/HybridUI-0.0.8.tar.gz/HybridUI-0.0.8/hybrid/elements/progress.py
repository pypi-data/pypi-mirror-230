from typing import List, Optional, Union, Literal
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Progress(Element):
    def __init__(
        self,
        strokeWidth=None,
        percent: Union[float, int] = None,
        status: Literal["normal", "exception", "active", "success"] = None,
        strokeLinecap: Literal["butt", "round", "square"] = None,
        showInfo: bool = None,
        size: int = None,
        type: Literal["line", "circle", "dashboard"] = None,
        strokeColor: dict=None,
        steps=None,
        gapDegree=None,
        gapPosition=None
    ):
        super().__init__(component='Progress')
        self.children =[]
        if percent is not None:
            self._props["percent"] = percent
        if status is not None:
            self._props["status"] = status
        if strokeLinecap is not None:
            self._props["strokeLinecap"] = strokeLinecap
        if showInfo is not None:
            self._props["showInfo"] = showInfo
        if size is not None:
            self._props["size"] = size

        if type == "line":
            self._props["type"] = "line"
            if steps is not None:
                self._props["steps"] = steps
            if strokeColor is not None:
                self._props["strokeColor"] = strokeColor

        elif type == "circle":
            self._props["type"] = "circle"
            if strokeColor is not None:
                self._props["strokeColor"] = strokeColor
            if strokeWidth is not None:
                self._props["strokeWidth"] =strokeWidth

        elif type == "dashboard":
            self._props["type"] = "dashboard"
            if strokeColor is not None:
                self._props["strokeColor"] = strokeColor
            if strokeWidth is not None:
                self._props["strokeWidth"] = strokeWidth
            if gapDegree is not None:
                self._props["gapDegree"] = gapDegree
            if gapPosition is not None:
                self._props["gapPosition"] = gapPosition
