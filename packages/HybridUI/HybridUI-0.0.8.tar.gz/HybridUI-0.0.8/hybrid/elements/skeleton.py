""" from typing import List
from ..element import Element



class Skeleton(Element):
    def __init__(
            self, 
            content = None,
            ):
        super().__init__(component='Skeleton')
        self.children = content

        if active is not None:
            self.props["active"] = None
        if avatar is not None:
            self.props["avatar"] = None
        if loading is not None:
            self.props["loading"] = None
        if paragraph is not None:
            self.props["paragraph"] = None
        if round is not None:
            self.props["round"] = None
        if title is not None:
            self.props["title"] = None
        if shape is not None:
            self.props["shape"] = None
        if size is not None:
            self.props["size"] = None
        if rows is not None:
            self.props["rows"] = None
        if width is not None:
            self.props["width"] = None
        if block is not None:
            self.props["block"] = None
        if shape is not None:
            self.props["shape"] = None
        if size is not None:
            self.props["size"] = None
        if is not None:
            self.props["size"] = None
 """