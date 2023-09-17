from typing import List, Union
from ..element import Element

class Badge(Element):
    """
    Badge component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        count: Union[str, int] = None,
        status: str = None,
        text: str = None,
        color=None,
        classNames=None,
        dot=None,
        offset=None,
        overflowCount=None,
        showZero=None,
        size=None,
        styles=None,
        title=None

    ):
        super().__init__(component='Badge')
        if color is not None:
            self._props["color"] = color
        if count is not None:
            self._props["count"] = count
        if classNames is not None:
            self._props["classNames"] = classNames
        if dot is not None:
            self._props["dot"] = dot
        if offset is not None:
            self._props["offset"] = offset
        if overflowCount is not None:
            self._props["overflowCount"] = overflowCount
        if showZero is not None:
            self._props["showZero"] = showZero
        if size is not None:
            self._props["size"] = size
        if status is not None:
            self._props["status"] = status
        if styles is not None:
            self._props["styles"] = styles
        if text is not None:
            self._props["text"] = text
        if title is not None:
            self._props["title"] = title

        self.content = content

class BadgeRibbon(Element):
    """
    Badge.Ribbon component (4.5.0+).
    """
    def __init__(
        self,
        content: List[Element] = None,
        color: str = None,
        placement: str = "start",
        text: str = None,
    ):
        super().__init__(component='BadgeRibbon')
        self.props["color"] = color
        self.props["placement"] = placement
        self.props["text"] = text
        self.props["styles"] = None
        self.props["classNames"] = None
        self.props["root"] = None
        self.props["indicator"] = None
        self.content = content
