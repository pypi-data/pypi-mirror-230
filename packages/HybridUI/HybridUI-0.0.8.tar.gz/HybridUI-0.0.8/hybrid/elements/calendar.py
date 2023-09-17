from typing import Optional
from ..element import Element

class Calendar(Element):
    """
    Calendar component.
    """
    def __init__(
        self,
        content: Element = None,
        dateCellRender: str = None,
        dateFullCellRender: str = None,
        defaultValue: Optional[str] = None,
        disabledDate: str = None,
        fullscreen: bool = False,
        headerRender: str = None,
        locale: dict = None,
        mode: str = None,
        monthCellRender: str = None,
        monthFullCellRender: str = None,
        validRange: list = None,
        value: Optional[str] = None,
        onChange: str = None,
        onPanelChange: str = None,
        onSelect: str = None,
    ):
        super().__init__(component='Calendar')
        if dateCellRender is not None:
            self._props["dateCellRender"] = dateCellRender
        if dateFullCellRender is not None:
            self._props["dateFullCellRender"] = dateFullCellRender
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabledDate is not None:
            self._props["disabledDate"] = disabledDate
        if fullscreen is not None:
            self._props["fullscreen"] = fullscreen
        if headerRender is not None:
            self._props["headerRender"] = headerRender
        if locale is not None:
            self._props["locale"] = locale
        if mode is not None:
            self._props["mode"] = mode
        if monthCellRender is not None:
            self._props["monthCellRender"] = monthCellRender
        if monthFullCellRender is not None:
            self._props["monthFullCellRender"] = monthFullCellRender
        if validRange is not None:
            self._props["validRange"] = validRange
        if value is not None:
            self._props["value"] = value
        if onChange is not None:
            self._props["onChange"] = onChange
        if onPanelChange is not None:
            self._props["onPanelChange"] = onPanelChange
        if onSelect is not None:
            self._props["onSelect"] = onSelect
        self.content = content
