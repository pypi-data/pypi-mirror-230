from typing import List
from ..element import Element

class BreadcrumbItem(Element):
    """
    Breadcrumb.Item component.
    """
    def __init__(self, content: List[Element] = None, **props):
        super().__init__(component='Breadcrumb.Item', **props)
        self.content = content

class Breadcrumb(Element):
    """
    Breadcrumb component.
    """
    def __init__(self, content: List[BreadcrumbItem] = None, separator: str = "/", **props):
        super().__init__(component='Breadcrumb', **props)
        self._props["separator"] = separator
        self.content = content
