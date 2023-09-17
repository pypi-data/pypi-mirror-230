from typing import List, Optional, Union, Callable
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Image(Element):
    """
    alt
    fallback
    height
    placeholder
    preview
    src
    width
    onError
    """
    def __init__(
        self,
        src: str = None,
        alt: Optional[str] = None,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        fallback: Optional[str] = None,
        placeholder: Optional[str] = None,
        preview: bool = True,
        onError: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Image')
        self.children = []

        if src is not None:
            self._props["src"] = src
        if alt is not None:
            self._props["alt"] = alt
        if width is not None:
            self._props["width"] = width
        if height is not None:
            self._props["height"] = height
        if fallback is not None:
            self._props["fallback"] = fallback
        if placeholder is not None:
            self._props["placeholder"] = placeholder
        if preview is not None:
            self._props["preview"] = preview
        if onError is not None:
            self._props["onError"] = onError
