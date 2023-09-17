from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Watermark(Element):
    """
    width	
    height	
    rotate	
    zIndex	
    image	
    content
    font	
    gap
    offset		
    Font
    color	font color	string	rgba(0,0,0,.15)	
    fontSize	font size	number	16	
    fontWeight	font weight	normal | light | weight | number	normal	
    fontFamily	font family	string	sans-serif	
    fontStyle	font style	none | normal | italic | oblique	normal
    """
    def __init__(
            self, 
            content: List[Element] = None,
            width = None,
            height = None,
            rotate = None,
            zIndex = None,
            image = None,
            font = None,
            gap = None,
            offset = None,
            Font = None,
            color = None,
            fontSize = None,
            fontWeight = None,
            fontFamily = None,
            fontStyle = None,
            
            ):
        super().__init__(component='Alert')

        if  width is not None:
            self._props["width"] = width
        if height is not None:
            self._props["height"] = height
        if rotate is not None:
            self._props["rotate"] = rotate
        if zIndex is not None:
            self._props["zIndex"] = zIndex
        if image is not None:
            self._props["image"] = image
        if content is not None:
            self._props["content"] = content
        if font is not None:
            self._props["font"] = font
        if gap is not None:
            self._props["gap"] = gap
        if offset is not None:
            self._props["offset"] = offset
        if Font is not None:
            self._props["Font"] = Font
        if color is not None:
            self._props["color"] = color
        if color is not None:
            self._props["color"] = color
        if fontSize is not None:
            self._props["fontSize"] = fontSize
        if fontWeight is not None:
            self._props["fontWeight"] = fontWeight
        if fontFamily is not None:
            self._props["fontFamily"] = fontFamily
        if fontStyle is not None:
            self._props["fontStyle"] = fontStyle
       
        self.component = content

        