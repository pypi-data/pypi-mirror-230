from typing import List, Dict
from ..element import Element



class Statistic(Element):

    def __init__(
            self, 
            content= None,
            decimalSeparator= None,
            formatter= None,
            groupSeparator= None,
            loading= None,
            precision= None,
            prefix= None,
            suffix= None,
            title= None,
            value= None,
            valueStyle= None):
        super().__init__(component='Statistic')
        self.children= []
        if decimalSeparator is not None:
            self._props["decimalSeparator"] = decimalSeparator
        if formatter is not None:
            self._props["formatter"] = formatter
        if groupSeparator is not None:
            self._props["groupSeparator"] = groupSeparator
        if loading is not None:
            self._props["loading"] = loading
        if precision is not None:
            self._props["precision"] = precision
        if prefix is not None:
            self._props["prefix"] = prefix
        if suffix is not None:
            self._props["suffix"] = suffix
        if title is not None:
            self._props["title"] = title
        if value is not None:
            self._props["value"] = value
        if valueStyle is not None:
            self._props["valueStyle"] = valueStyle


class CountdownStatistic(Element):
    def __init__(
            self, 
            content: List[Element] = None, 
            format="HH:mm:ss",
            prefix= None,
            suffix=None,
            title=None,
            value= None, 
            valueStyle= None,
            onFinish= None,
            onChange= None):
        super().__init__(component='Statistic')
        self.children = content
        if format is not None:
            self._props["format"] = format
        if prefix is not None:
            self._props["prefix"] = prefix
        if suffix is not None:
            self._props["suffix"] = suffix
        if title is not None:
            self._props["title"] = title
        if value is not None:
            self._props["value"] = value
        if valueStyle is not None:
            self._props["valueStyle"] = valueStyle
        if onFinish is not None:
            self._props["onFinish"] = onFinish
        if onChange is not None:
            self._props["onChange"] = onChange
