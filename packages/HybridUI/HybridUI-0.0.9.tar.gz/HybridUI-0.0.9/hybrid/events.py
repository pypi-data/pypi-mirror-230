from dataclasses import dataclass
import uuid



@dataclass
class MouseEvent:
    listner_id: uuid.uuid4()
    isTrusted: bool
    altKey: bool
    altitudeAngle: float
    azimuthAngle: float
    bubbles: bool
    button: int
    buttons: int
    cancelBubble: bool
    cancelable: bool
    clientX: int
    clientY: int
    composed: bool
    ctrlKey: bool
    defaultPrevented: bool
    detail: int
    eventPhase: int
    height: int
    isPrimary: bool
    layerX: int
    layerY: int
    metaKey: bool
    movementX: int
    movementY: int
    offsetX: int
    offsetY: int
    pageX: int
    pageY: int
    pointerId: int
    pointerType: str
    pressure: int
    returnValue: bool
    screenX: int
    screenY: int
    shiftKey: bool
    sourceCapabilities: bool
    tangentialPressure: int
    tiltX: int
    tiltY: int
    timeStamp: float
    toElement: str
    twist: int
    type: str
    which: int
    width: int
    x: int
    y: int
