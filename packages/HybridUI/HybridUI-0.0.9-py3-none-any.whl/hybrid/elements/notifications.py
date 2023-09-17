from typing import Any, Dict, List, Union, Callable, Optional

from ..element import Element





class SuccessNotifications(Element):

    def __init__(
        self,
        duration: int = 5,
        message: str = "",
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["duration"] = duration
        self.props["message"] = message
        self.props["onClose"] = onClose





class ErrorNotifications(Element):
    def __init__(
        self,
        error: str = "",
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["error"] = error
        self.props["onClose"] = onClose





class InfoNotifications(Element):
    def __init__(
        self,
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["info"] = "info"
        self.props["onClose"] = onClose





class WarningNotifications(Element):

    def __init__(
        self,
        warning: str = "",
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["warning"] = warning
        self.props["onClose"] = onClose



class OpenNotifications(Element):
    def __init__(
        self,
        content: str = "",
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["content"] = content
        self.props["onClose"] = onClose




        
class DestroyNotifications(Element):
    def __init__(
        self,
        content: str = "",
        onClose: Optional[Callable[[], None]] = None,
    ):
        super().__init__(component='Alert')

        self.props["content"] = content
        self.props["onClose"] = onClose
