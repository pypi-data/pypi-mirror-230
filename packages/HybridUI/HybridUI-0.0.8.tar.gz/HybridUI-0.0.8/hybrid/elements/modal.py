from typing import List, Optional, Union, Callable
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Modal(Element):

    def __init__(
        self,
        content= None,
        title: Union[str, Element] = None,
        visible: bool = None,
        closable: bool = None,
        maskClosable: bool = None,
        width: Union[int, str] = None,
        centered: bool = None,
        footer = None,
        okText: str = None,
        cancelText: str = None,
        onOk = None,
        onCancel= None,
        afterOpenChange= None,
        confirmLoading: bool = None,
        destroyOnClose: bool = None,
        mask: bool = None,
        keyboard: bool = None,
        maskStyle: dict = None,
        style: dict = None,
        wrapClassName: str = None,
        zIndex: int = None,
        okType= None,
        okButtonProps= None,
        modalRender= None,
        getContainer= None,
        focusTriggerAfterClose= None,
        closeIcon= None,
        cancelButtonProps= None,
        bodyStyle= None,
        afterClose= None,
        open= None
    ):
        super().__init__(component='Modal')
        self.children=content
        
        if title is not None:
            self._props["title"] = title

        if open is not None:
            self._props["open"] = open

        if visible is not None:
            self._props["visible"] = visible
        if closable is not None:
            self._props["closable"] = closable
        if maskClosable is not None:
            self._props["maskClosable"] = maskClosable
        if width is not None:
            self._props["width"] = width
        if centered is not None:
            self._props["centered"] = centered
        if footer is not None:
            self._props["footer"] = footer
        if okText is not None:
            self._props["okText"] = okText
        if cancelText is not None:
            self._props["cancelText"] = cancelText
        if onOk is not None:
            self._props["onOk"] = onOk
        if onCancel is not None:
            self._props["onCancel"] = onCancel
        if afterOpenChange is not None:
            self._props["afterOpenChange"] = afterOpenChange
        if confirmLoading is not None:
            self._props["confirmLoading"] = confirmLoading
        if destroyOnClose is not None:
            self._props["destroyOnClose"] = destroyOnClose
        if mask is not None:
            self._props["mask"] = mask
        if keyboard is not None:
            self._props["keyboard"] = keyboard
        if maskStyle is not None:
            self._props["maskStyle"] = maskStyle
        if style is not None:
            self._props["style"] = style
        if wrapClassName is not None:
            self._props["wrapClassName"] = wrapClassName
        if zIndex is not None:
            self._props["zIndex"] = zIndex
        if okType is not None:
            self._props["okType"] = okType
        if okButtonProps is not None:
            self._props["okButtonProps"] = okButtonProps
        if modalRender is not None:
            self._props["modalRender"] = modalRender
        if getContainer is not None:
            self._props["getContainer"] = getContainer
        if focusTriggerAfterClose is not None:
            self._props["focusTriggerAfterClose"] = focusTriggerAfterClose
        if closeIcon is not None:
            self._props["closeIcon"] = closeIcon
        if cancelButtonProps is not None:
            self._props["cancelButtonProps"] = cancelButtonProps
        if bodyStyle is not None:
            self._props["bodyStyle"] = bodyStyle
        if afterClose is not None:
            self._props["afterClose"] = afterClose
