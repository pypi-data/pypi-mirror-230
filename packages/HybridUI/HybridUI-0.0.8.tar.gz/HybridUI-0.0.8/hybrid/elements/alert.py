from typing import List, Union
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Alert(Element):
    """
    action	
    afterClose	
    banner	
    closeIcon	 	
    description	
    icon		
    message	
    showIcon	
    type	
    onClose	

    Alert.ErrorBoundary

    description	
    message	
    """
    def __init__(
        self,
        content= None,
        message: Union[str, Element] = None,
        type: str = None,
        showIcon: bool = None,
        action= None,	
        afterClose= None,
        banner= None,
        closeIcon= None,	 	
        description= None,	
        icon= None,
        onClose= None,	

    ):
        super().__init__(component='Alert')
        if content is not None:
            self._props["content"] = content
        if message is not None:
            self._props["message"] = message
        if type is not None:
            self._props["type"] = type
        if showIcon is not None:
            self._props["showIcon"] = showIcon
        if action is not None:
            self._props["action"] = action
        if afterClose is not None:
            self._props["afterClose"] = afterClose
        if banner is not None:
            self._props["banner"] = banner
        if closeIcon is not None:
            self._props["closeIcon"] = closeIcon
        if description is not None:
            self._props["description"] = description
        if icon is not None:
            self._props["icon"] = icon
        if onClose is not None:
            self._props["onClose"] = onClose
 
     