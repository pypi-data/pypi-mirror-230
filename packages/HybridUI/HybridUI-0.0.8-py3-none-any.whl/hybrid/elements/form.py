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
        self.props["colon"] = colon
        self.props["disabled"] = disabled
        self.props["fields"] = fields
        self.props["form"] = form
        self.props["initialValues"] = initialValues
        self.props["labelAlign"] = labelAlign
        self.props["labelWrap"] = labelWrap
        self.props["labelCol"] = labelCol
        self.props["layout"] = layout
        self.props["name"] = name
        self.props["preserve"] = preserve,
        self.props["requiredMark"] = requiredMark
        self.props["scrollToFirstError"] = scrollToFirstError
        self.props["size"] = size
        self.props["validateMessages"] = validateMessages
        self.props["validateTrigger"] = validateTrigger
        self.props["wrapperCol"] = wrapperCol
        self.props["onFieldsChange"] = onFieldsChange
        self.props["onFinish"] = onFinish
        self.props["onFinishFailed"] = onFinishFailed
        self.props["onValuesChange"] = onValuesChange
        self.content = content
