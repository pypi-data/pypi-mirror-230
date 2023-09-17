from typing import List, Any, Callable, Optional
from ..element import Element



class Player(Element):

  
    def __init__(
        self,
        url = None,
        playing	 = None,
        loop = None,	
        controls = None,	
        light = None,	
        volume = None,	
        muted = None,	
        playbackRate = None,	
        width = None,	
        height = None,	
        style = None,	
        progressInterval = None,	
        playsinline = None,	
        pip = None,	
        stopOnUnmount = None,	
        fallback = None,	
        wrapper = None,	
        playIcon = None,	
        previewTabIndex	 = None,
        config = None,		
        onReady	 = None,
        onStart = None,	
        onPlay = None,	
        onProgress = None,	
        onDuration = None,	
        onPause = None,
        onBuffer = None,	
        onBufferEnd = None,	
        onSeek = None,	
        onPlaybackRateChange = None,	
        onPlaybackQualityChange = None,	
        onEnded = None,	
        onError = None,
        onClickPreview = None,	
        onEnablePIP = None,	
        onDisablePIP = None,

    ):
        super().__init__(component='Player')
        self.children= []
        if url is not None:
            self._props["url"] = url
        if playing is not None:
            self._props["playing"] = playing
        if loop is not None:
            self._props["loop"] = loop
        if controls is not None:
            self._props["controls"] = controls
        if light is not None:
            self._props["light"] = light
        if volume is not None:
            self._props["volume"] = volume
        if muted is not None:
            self._props["muted"] = muted
        if playbackRate is not None:
            self._props["playbackRate"] = playbackRate
        if width is not None:
            self._props["width"] = width
        if height is not None:
            self._props["height"] = height
        if progressInterval is not None:
            self._props["progressInterval"] = progressInterval
        if playsinline is not None:
            self._props["playsinline"] = playsinline
        if pip is not None:
            self._props["pip"] = pip
        if stopOnUnmount is not None:
            self._props["stopOnUnmount"] = stopOnUnmount
        if fallback is not None:
            self._props["fallback"] = fallback
        if wrapper is not None:
            self._props["wrapper"] = wrapper
        if playIcon is not None:
            self._props["playIcon"] = playIcon
        if previewTabIndex is not None:
            self._props["previewTabIndex"] = previewTabIndex
        if config is not None:
            self._props["config"] = config
        if onReady is not None:
            self._props["onReady"] = onReady
        if onStart is not None:
            self._props["onStart"] = onStart
        if onPlay is not None:
            self._props["onPlay"] = onPlay
        if onProgress is not None:
            self._props["onProgress"] = onProgress
        if onDuration is not None:
            self._props["onDuration"] = onDuration
        if onPause is not None:
            self._props["onPause"] = onPause
        if onBuffer is not None:
            self._props["onBuffer"] = onBuffer
        if style is not None:
            self._props["style"] = style
        if onBufferEnd is not None:
            self._props["onBufferEnd"] = onBufferEnd
        if onSeek is not None:
            self._props["onSeek"] = onSeek
        if onPlaybackRateChange is not None:
            self._props["onPlaybackRateChange"] = onPlaybackRateChange
        if onPlaybackQualityChange is not None:
            self._props["onPlaybackQualityChange"] = onPlaybackQualityChange
        if onEnded is not None:
            self._props["onEnded"] = onEnded
        if onError is not None:
            self._props["onError"] = onError
        if onClickPreview is not None:
            self._props["onClickPreview"] = onClickPreview
        if onEnablePIP  is not None:
            self._props["onEnablePIP"] = onEnablePIP
        if onDisablePIP is not None:
            self._props["onDisablePIP"] = onDisablePIP
      