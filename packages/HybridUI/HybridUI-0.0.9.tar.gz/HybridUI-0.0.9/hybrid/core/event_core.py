import uuid
from inspect import signature 
from distutils.command.upload import upload
import uuid
import inspect
import os
import time
from pathlib import Path
from inspect import signature
from cgitb import reset
from faulthandler import disable
import json
from typing import Dict, Any
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from fastapi import Request



class SyntheiticEvent:
    uuid_callback_map = {}
    callback_uuid_map = {}
    def handler(self, callback):
        if callback is None:
            return None
        if callback in self.callback_uuid_map:
            return self.callback_uuid_map[callback]
        else:
            cb_uuid = str(uuid.uuid1())
            self.uuid_callback_map[cb_uuid] = callback
            self.callback_uuid_map[callback] = cb_uuid
            return cb_uuid
    def listner(self, uuid, args):
        if uuid in self.uuid_callback_map:
            method = self.uuid_callback_map[uuid]
            param_length = len(signature(method).parameters)
            return method(*args[:param_length])
        else:
            # TODO: Return an error to the frontend
            return None





def main1():
    print('Hallo')



def main2(a,b):
    print(a + b)
""" 
print('____________________________ UUID 1 ___________________________________')
uuid1 = callbackRegistry.uuid_for_callback(main1)
print(uuid1)

print('____________________________ UUID 2 ___________________________________')
uuid2 = callbackRegistry.uuid_for_callback(main2)
print(uuid2)

print('____________________________ Aufruf der erste Funktion UUID 1 ___________________________________')
callbackRegistry.make_callback(uuid1, args=[])  # Pass an empty list as arguments
print('____________________________ Aufruf der erste Funktion UUID 2 ___________________________________')
callbackRegistry.make_callback(uuid2, args=[1, 2])  # Pass a list of arguments """






