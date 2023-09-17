from typing import Any, List, Optional, Union, Callable, Dict
from ..element import Element, JSONSerializable
from ..interface import outbox
from ..embedded_encoder import ElementJSONEncoder
import json
# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Modal:

    def __init__(
        self,
        content= None,
        title:Element = None,
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
        self.as_dict()

    def as_dict(self) -> Dict[str, Any]:
        return {x: self.__dict__[x] for x in self.__dict__ if self.__dict__[x] is not None}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        initilmodal = self.as_dict()
        elements = json.dumps(initilmodal, default=lambda o: o.__class__.__name__, indent=4)
        return outbox('openmodal', data=elements)