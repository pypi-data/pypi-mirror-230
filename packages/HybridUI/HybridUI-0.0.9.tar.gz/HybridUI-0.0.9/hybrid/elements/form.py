from typing import List, Optional, Callable, Any, Dict
from ..element import Element

class Form(Element):
    """
    Form component.
    """
    def __init__(
        self,
        content: List[Element] = None,
        layout: str = "vertical",
        form: Any = None,
        name: str = None,
        initialValues: Dict[str, Any] = None,
        onFinish: Callable = None,
        onFinishFailed: Callable = None,
        disabled =None,
        colon=None,
        fields=None,
        labelAlign=None,
        labelWrap=None,
        labelCol=None,
        preserve=None,
        requiredMark=None,
        scrollToFirstError=None,
        size=None,
        validateMessages=None,
        validateTrigger=None,
        wrapperCol=None,
        onFieldsChange=None,
        onValuesChange=None,
        
    ):
        super().__init__(component='Form')
        self._props["colon"] = colon
        self._props["disabled"] = disabled
        self._props["fields"] = fields
        self._props["form"] = form
        self._props["initialValues"] = initialValues
        self._props["labelAlign"] = labelAlign
        self._props["labelWrap"] = labelWrap
        self._props["labelCol"] = labelCol
        self._props["layout"] = layout
        self._props["name"] = name
        self._props["preserve"] = preserve,
        self._props["requiredMark"] = requiredMark
        self._props["scrollToFirstError"] = scrollToFirstError
        self._props["size"] = size
        self._props["validateMessages"] = validateMessages
        self._props["validateTrigger"] = validateTrigger
        self._props["wrapperCol"] = wrapperCol
        self._props["onFieldsChange"] = onFieldsChange
        self._props["onFinish"] = onFinish
        self._props["onFinishFailed"] = onFinishFailed
        self._props["onValuesChange"] = onValuesChange
        self.content = content
