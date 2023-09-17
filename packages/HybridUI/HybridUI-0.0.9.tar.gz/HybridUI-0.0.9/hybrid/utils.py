from typing import List, TypedDict

class Style(TypedDict):
    name: str
    value: str

styles: List[Style] = [
    {"name": "color", "value": "red"},
    {"name": "fontSize", "value": "16px"}
]