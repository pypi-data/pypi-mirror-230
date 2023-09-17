from typing import List
from ..element import Element
from .. import system_spezifisch


class Slider(Element):

    def __init__(
            self,
            autoAdjustOverflow=None,
            autoFocus=None,
            defaultValue=None,
            disabled=None,
            keyboard=None,
            dots=None,
            included=None,
            marks=None,
            max=None,
            min=None,
            range=None,
            reverse=None,
            step=None, 
            tooltip=None, 
            value=None,
            vertical=None,
            onAfterChange=None,
            onChange=None,
            trackStyle=None,
            railStyle=None,
            handleStyle= None
        ):
        super().__init__(component='Slider')
        
        self.children = ['']
        
        if autoAdjustOverflow is not None:
            self._props["autoAdjustOverflow"] = autoAdjustOverflow
        if autoFocus is not None:
            self._props["autoFocus"] = autoFocus
        if keyboard is not None:
            self._props["keyboard"] = keyboard
        if dots is not None:
            self._props["dots"] = dots
        if marks is not None:
            self._props["marks"] = marks
        if range is not None:
            self._props["range"] = range
        if reverse is not None:
            self._props["reverse"] = reverse
        if tooltip is not None:
            self._props["tooltip"] = tooltip
        if vertical is not None:
            self._props["vertical"] = vertical
        if onAfterChange is not None:
            self._props["onAfterChange"] = onAfterChange
        if trackStyle is not None:
            self._props["trackStyle"] = trackStyle
        if railStyle is not None:
            self._props["railStyle"] = railStyle
        if handleStyle is not None:
            self._props["handleStyle"] = handleStyle
        if included is not None:
            self._props["included"] = included
        if step is not None:
            self._props["step"] = step
        if max is not None:
            self._props["max"] = max
        if min is not None:
            self._props["min"] = min
        if value is not None:
            self._props["value"] = value
        if defaultValue is not None:
            self._props["defaultValue"] = defaultValue
        if disabled is not None:
            self._props["disabled"] = disabled

        if onChange:
            handel = self.on(onChange)
            self._props["onChange"] = handel
        
    def onchange_value(self):
        if system_spezifisch.slider_onchange_value:
            return system_spezifisch.slider_onchange_value[0]

