from __future__ import annotations
import json
import uuid
from typing import List, Dict, Any
from typing import Protocol, runtime_checkable, Optional, Iterator, Callable
import re
import json
from abc import ABC
from .core.event_core import SyntheiticEvent
import uuid
from typing import List, Dict, Any, Union, Protocol, runtime_checkable
from typing_extensions import Self
from . import globals
PROPS_PATTERN = re.compile(r'([:\w\-]+)(?:=(?:("[^"\\]*(?:\\.[^"\\]*)*")|([\w\-.%:\/]+)))?(?:$|\s)')


@runtime_checkable
class JSONSerializable(Protocol):
    def as_dict(self) -> Dict[str, Any]:
        ...


class Element(SyntheiticEvent):
    def __init__(self, component: str, children=None, update_client:bool = None):
        self.key = str(uuid.uuid4())
        self.component: str = component
        self._props: Dict[str, Any] = {}
        self.children: List[Union[str, 'Element']] = children if children is not None else []
    

        if update_client == True:
            globals.update_component.append[self.key]

    

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def as_dict(self) -> Dict[str, Any]:
        child = {x: self.__dict__[x] for x in self.__dict__ if self.__dict__[x] is not None}
        data = {
            "key":self.key,
            "component": self.component,
            "props": self._props,
            "children": [child.as_dict() if isinstance(child, Element) else child for child in self.children]
        }
        #[child.as_dict() if isinstance(child, Element) else child for child in self.children]
        #py = json.dumps(data, default=lambda o: o.as_dict() if isinstance(o, JSONSerializable)  else None, indent=4, cls=ElementJSONEncoder)
        return data
    
    @staticmethod
    def _parse_props(name: Optional[str]) -> Dict[str, Any]:
        dictionary = {}
        for match in PROPS_PATTERN.finditer(name or ''):
            key = match.group(1)
            value = match.group(2) or match.group(3)
            if value and value.startswith('"') and value.endswith('"'):
                value = json.loads(value)
            dictionary[key] = value or True
        return dictionary

    def props(self, add: Optional[str] = None, *, remove: Optional[str] = None) -> Self:
        needs_update = False
        for key in self._parse_props(remove):
            if key in self._props:
                needs_update = True
                del self._props[key]
        for key, value in self._parse_props(add).items():
            if self._props.get(key) != value:
                needs_update = True
                self._props[key] = value
        if needs_update:
            self.update()
        return self
    
    def on(self, handler: Callable):
        listner_id = self.handler(handler)
        return listner_id


class ElementJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Element):
            return obj.as_dict()
        return super().default(obj)






class ReactNode(Element):
   def __init__(self, component: str, children=None, style= None):
       super().__init__(component)
       self.children= children
       self._props['style'] = style