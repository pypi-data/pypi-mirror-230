from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from ..element import Element




class Button(Element):
    def __init__(
        self, 
        block= None,
        classNames= None,
        danger= None,
        disabled= None,
        ghost= None,
        href= None,
        htmlType= None,
        icon= None,
        loading= None,
        shape= None,
        size= None,
        styles= None,
        target= None,
        type='primary',
        onClick= None,
        text= None
        ):
        super().__init__(component='Button')
       
        self.children=[text]
        if type is not None:
            self._props["type"]=type
        if block is not None:
            self._props["block"]=block
        if classNames is not None:
            self._props["classNames"]=classNames
        if danger is not None:
            self._props["danger"]=danger
        if disabled is not None: 
            self._props["disabled"]=disabled
        if ghost is not None: 
            self._props["ghost"]=ghost
        if href is not None:
            self._props["href"]=href
        if htmlType is not None:
            self._props["htmlType"]=htmlType
        if icon is not None:
            self._props["icon"]=icon
        if loading is not None:
            self._props["loading"]=loading
        if shape is not None:
            self._props["shape"]=shape
        if size is not None:
            self._props["size"]=size
        if styles is not None:
            self._props["styles"]=styles
        if target is not None:
            self._props["target"]=target
        
        if onClick:
            regester_handler = self.on(onClick)
            self._props["onClick"]=regester_handler

        