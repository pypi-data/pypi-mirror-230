from typing import List, Optional, Union, Callable, Any
from ..element import Element

class Drawer(Element):
    """
    autoFocus
    afterOpenChange
    bodyStyle
    className
    closeIcon
    contentWrapperStyle
    destroyOnClose
    extra
    footer
    footerStyle
    forceRender
    getContainer
    headerStyle
    height
    keyboard
    mask
    maskClosable
    maskStyle
    placement
    push
    rootStyle
    style
    size
    title
    open
    width
    zIndex
    onClose
    """
    def __init__(
        self,
        content,
        title: Union[str, Element] = None,
        placement: str = None,
        closable: bool = None,
        onClose: Optional[Callable[[], None]] = None,
        autoFocus: bool = None,
        afterOpenChange: Callable = None,
        bodyStyle: dict = None,
        className: str = None,
        closeIcon: Any = None,
        contentWrapperStyle: dict = None,
        destroyOnClose: bool = None,
        extra: Element = None,
        footer: Element = None,
        footerStyle: dict = None,
        forceRender: bool = None,
        getContainer: Union[str, Callable] = None,
        headerStyle: dict = None,
        height: Union[str, int] = None,
        keyboard: bool = None,
        mask: bool = None,
        maskClosable: bool = None,
        maskStyle: dict = None,
        push: bool = None,
        rootStyle: dict = None,
        style: dict = None,
        size: str = None,
        zIndex: int = None,
        width: Union[str, int] = None,
    ):
        super().__init__(component='Drawer')
        self.children= content
        if title is not None:    
            self._props["title"] = title
        if placement is not None:    
            self._props["placement"] = placement
        if closable is not None:    
            self._props["closable"] = closable
        if onClose is not None:    
            self._props["onClose"] = onClose
        if autoFocus is not None:    
            self._props["autoFocus"] = autoFocus
        if afterOpenChange is not None:    
            self._props["afterOpenChange"] = afterOpenChange
        if bodyStyle is not None:    
            self._props["bodyStyle"] = bodyStyle
        if className is not None:    
            self._props["className"] = className
        if closeIcon is not None:    
            self._props["closeIcon"] = closeIcon
        if contentWrapperStyle is not None:    
            self._props["contentWrapperStyle"] = contentWrapperStyle
        if destroyOnClose is not None:    
            self._props["destroyOnClose"] = destroyOnClose
        if extra is not None:    
            self._props["extra"] = extra
        if footer is not None:    
            self._props["footer"] = footer
        if footerStyle is not None:    
            self._props["footerStyle"] = footerStyle
        if forceRender is not None:    
            self._props["forceRender"] = forceRender
        if getContainer is not None:    
            self._props["getContainer"] = getContainer
        if headerStyle is not None:    
            self._props["headerStyle"] = headerStyle
        if height is not None:    
            self._props["height"] = height
        if keyboard is not None:    
            self._props["keyboard"] = keyboard
        if mask is not None:    
            self._props["mask"] = mask
        if maskClosable is not None:    
            self._props["maskClosable"] = maskClosable
        if maskStyle is not None:    
            self._props["maskStyle"] = maskStyle
        if push is not None:    
            self._props["push"] = push
        if rootStyle is not None:    
            self._props["rootStyle"] = rootStyle
        if style is not None:    
            self._props["style"] = style
        if size is not None:    
            self._props["size"] = size
        if zIndex is not None:    
            self._props["zIndex"] = zIndex
        if width is not None:    
            self._props["width"] = width
