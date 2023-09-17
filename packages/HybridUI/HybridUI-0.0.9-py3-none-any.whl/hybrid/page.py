from typing import Optional, Union, Callable
from fastapi import APIRouter
from pathlib import Path
from fastapi import APIRouter
from pathlib import Path



class Page(APIRouter):
    def page(self,
             path: str, *,
             title: Optional[str] = None,
             viewport: Optional[str] = None,
             favicon: Optional[Union[str, Path]] = None,
             dark: Optional[bool] = ...,
             response_timeout: float = 3.0,
             **kwargs,
             ) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def remove_route(self, path: str) -> None:
        self.routes[:] = [r for r in self.routes if getattr(r, 'path', None) != path]