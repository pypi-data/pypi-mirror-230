from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from ..element import Element






class Typography(Element):
    def __init__(
            self,
            code= None, 
            copyable= None,
            delete= None,
            disabled= None,
            editable= None,
            ellipsis= None,
            level= None,
            mark= None,
            onClick= None,
            italic= None,
            type= None,
            underline= None, 
            content = None):
        super().__init__(component='Typography')
        if code is not None:
            self._props["code"] = code
        if copyable is not None:
            self._props["copyable"] = copyable
        if delete is not None:
            self._props["delete"] = delete
        if disabled is not None:
            self._props["disabled"] = disabled
        if editable is not None:
            self._props["editable"] = editable
        if ellipsis is not None:
            self._props["ellipsis"] = ellipsis
        if level is not None:
            self._props["level"] = level
        if mark is not None:
            self._props["mark"] = mark
        if onClick is not None:
            self._props["onClick"] = onClick
        if italic is not None:
            self._props["italic"] = italic
        if type is not None:
            self._props["type"] = type
        if underline is not None:
            self._props["underline"] = underline
        self.children = [content]





class Title(Element):
    """
    Typography(Title):

    code	
    copyable
    delete
    disabled	
    editable
    ellipsis
    level
    mark	
    onClick
    italic
    type
    underline
    """
    def __init__(
            self,
            code= None, 
            copyable= None,
            delete= None,
            disabled= None,
            editable= None,
            ellipsis= None,
            level= None,
            mark= None,
            onClick= None,
            italic= None,
            type= None,
            underline= None, 
            content = None):
        super().__init__(component='Title')
        
        if code is not None:
            self._props["code"] = code
        if copyable is not None:
            self._props["copyable"] = copyable
        if delete is not None:
            self._props["delete"] = delete
        if disabled is not None:
            self._props["disabled"] = disabled
        if editable is not None:
            self._props["editable"] = editable
        if ellipsis is not None:
            self._props["ellipsis"] = ellipsis
        if level is not None:
            self._props["level"] = level
        if mark is not None:
            self._props["mark"] = mark
        if onClick is not None:
            self._props["onClick"] = onClick
        if italic is not None:
            self._props["italic"] = italic
        if type is not None:
            self._props["type"] = type
        if underline is not None:
            self._props["underline"] = underline
        self.children = [content]

        








class Text(Element):
    """
    Typography(Text):

    code
    copyable
    delete
    disabled	
    editable
    ellipsis
    keyboard
    mark	
    onClick
    strong	
    italic
    type
    underline

    
    """
    def __init__(
            self, 
            content= None,
            code=None,
            copyable=None,
            delete=None,
            disabled=None,
            editable=None,
            ellipsis=None,
            strong=None,
            mark=None,
            onClick=None,
            italic=None,
            type=None,
            underline=None,
            keyboard=None
            
            ):
        super().__init__(component='Text')
        
        if code is not None:
            self._props["code"] = code
        if copyable is not None:
            self._props["copyable"] = copyable
        if delete is not None:
            self._props["delete"] = delete
        if disabled is not None:
            self._props["disabled"] = disabled
        if editable is not None:
            self._props["editable"] = editable
        if ellipsis is not None:
            self._props["ellipsis"] = ellipsis
        if strong is not None:
            self._props["strong"] = strong
        if mark is not None:
            self._props["mark"] = mark
        if onClick is not None:
            self._props["onClick"] = onClick
        if italic is not None:
            self._props["italic"] = italic
        if type is not None:
            self._props["type"] = type
        if underline is not None:
            self._props["underline"] = underline
        if keyboard is not None:
            self._props["keyboard"] = keyboard
        self.children = [content]





class Paragraph(Element):
    """
    Typography(Paragraph):

    code
    copyable
    delete	
    disabled	
    editable
    ellipsis
    mark
    onClick		
    strong
    italic
    type
    underline

    
    """
    def __init__(
            self, 
            content= None,
            code= None,
            copyable= None,
            delete= None,
            disabled= None,
            editable= None,
            onClick= None,
            mark= None,
            italic= None,
            underline= None,
            type= None,
            ellipsis=None,
            ):
        super().__init__(component='Paragraph')
        if code is not None:
            self._props["code"] = code
        if copyable is not None:
            self._props["copyable"] = copyable
        if delete is not None:
            self._props["delete"] = delete
        if disabled is not None:
            self._props["disabled"] = disabled
        if editable is not None:
            self._props["editable"] = editable
        if ellipsis is not None:
            self._props["ellipsis"] = ellipsis
        if mark is not None:
            self._props["mark"] = mark
        if onClick is not None:
            self._props["onClick"] = onClick
        if italic is not None:
            self._props["italic"] = italic
        if type is not None:
            self._props["type"] = type
        if underline is not None:
            self._props["underline"] = underline
        self.children = [content]
