from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_socketio import SocketManager
from pathlib import Path
from typing import Dict
import json
import math
from .core.electron import FlaskUI
from .core.event_core import  SyntheiticEvent
from dateutil.relativedelta import relativedelta
import uvicorn
from .page import Page
import threading
import webbrowser
from uvicorn import Config, Server
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union
#from language import Language
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Literal
from . import globals
from .element import Element, JSONSerializable
from .events import MouseEvent
from fastapi import Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile
import shutil
from starlette.responses import FileResponse 
from starlette.exceptions import HTTPException as StarletteHTTPException
from .core.event_core_ import EventListener
from .embedded_encoder import ElementJSONEncoder
import os
from . import system_spezifisch
from . import globals
import random
import datetime
import time
import random
import asyncio
from .core.chrome_engine import BrowserModule
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from . import __version__

class UI(SyntheiticEvent):

    def __init__(
        self, 
        layout: List[Element]= None,
        host: Optional[str] = 'localhost', 
        port: int = 8000,
        title: str = 'Hybrid',
        viewport: str = 'width=device-width, initial-scale=1',
        favicon: Optional[Union[str, Path]] = 'favicon,icon',
        dark: Optional[bool] = False,
        scrolling= None,
        binding_refresh_interval: float = 0.1,
       
        window_size: Optional[Tuple[int, int]] = None,
        fullscreen: bool = False,
        reload: bool = True,
        uvicorn_logging_level: str = 'warning',
        uvicorn_reload_dirs: str = '.',
        uvicorn_reload_includes: str = '*.py',
        uvicorn_reload_excludes: str = '.*, .py[cod], .sw.*, ~*',
        exclude: str = '',
        upload_folder= None,
        globale_ui_style=None,
        native_view = False,
        storage_secret: Optional[str] = None,
   
    ) -> None:
        
        self.upload_folder = upload_folder
        self.app = globals.app =FastAPI()
        self.socket_manager = SocketManager(app=self.app, mount_location='/hybrid/', json=json)
        self.sio =globals.sio= self.socket_manager._sio
        self.templates = Jinja2Templates(Path(__file__).parent / 'templates')  # Set the correct directory for your templates
         # Set the correct directory for your static files
    
        self.static_files = StaticFiles(
            directory=(Path(__file__).parent / 'static').resolve(),
            follow_symlink=True,
        )
        self.app.mount(f'/static', self.static_files, name='static')
        self.app.add_middleware(GZipMiddleware)
        self.page_router = Page()
        self.socket_extra_headers: Dict[str, Any] = {}
        self.title = title
        self.globale_ui_style =globale_ui_style
        self.globale_ui_style_content= self.read_data_file(self.globale_ui_style)
        self.host = host
        self.port = port
        self.viewport = viewport
        self.favicon = favicon
        self.dark = dark
        #self.language = language
        self.binding_refresh_interval = binding_refresh_interval
        self.window_size = window_size
        self.fullscreen = fullscreen
        self.uvicorn_logging_level = uvicorn_logging_level
        self.uvicorn_reload_dirs = uvicorn_reload_dirs
        self.uvicorn_reload_includes = uvicorn_reload_includes
        self.uvicorn_reload_excludes = uvicorn_reload_excludes
        self.exclude = exclude
        self.native_view = native_view
        self.reload = reload
        self.storage_secret = storage_secret
        self.app_settings = 'hybrid.globals:app'
        self.layout = layout
        self.scrolling = scrolling
        self.app.add_middleware(GZipMiddleware)
        self.app.add_middleware(
           CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/")
        async def render_template(request: Request,status_code: int = 200)-> Response:
            prefix = request.headers.get('X-Forwarded-Prefix', request.scope.get('root_path', ''))
            return self.templates.TemplateResponse(
                "index.html", {
                    "request": request,
                    'prefix':prefix, 
                    'version':__version__,
                    'title':self.title,
                    'viewport': self.viewport,
                    }, status_code, {'Cache-Control': 'no-store', 'X-Hybrid-Content': 'page'})

        @self.app.get("/initialapp")
        async def build_response(request: Request, status_code: int = 200)-> Response:
            prefix = request.headers.get('X-Forwarded-Prefix', request.scope.get('root_path', ''))
            socket_io_js_extra_headers: Dict = {}
            socket_io_js_transports: List[Literal['websocket', 'polling']] = ['websocket', 'polling']
            client_id = str(1)     
            initial_app_layout = Element(component="Layout", children=[layout])
            elements = json.dumps(initial_app_layout, default=lambda o: o.as_dict() if isinstance(o, JSONSerializable)  else None, indent=4, cls=ElementJSONEncoder)
            data = {
                'query': client_id,
                'prefix': prefix,
                'config': elements,
                'socket_io_js_extra_headers': socket_io_js_extra_headers,
                'socket_io_js_transports': socket_io_js_transports,
                'dark_mode':self.dark,
                'globale_ui_style':self.globale_ui_style_content
            }
            return data


        @self.app.post("/api/upload")
        async def post_upload(upload: UploadFile):
            with open(os.path.join(self.upload_folder, upload.filename), 'wb') as buffer:
                file = shutil.copyfileobj(upload.file, buffer)
                print(file)

        @self.app.get("/get_component_key")
        def check_update(request: Request, status_code: int = 200)-> Response:
            
            return {"componentKey": globals.update_component}

    
        @self.sio.on("browserconct")
        async def on_browserconct(sid):
            print(f"Client {sid} connected")
            return 'ok'

        @self.sio.on("disconnect")
        async def disconnect(sid):
            print(f"Client {sid} disconnected")

        @self.sio.on("event")
        async def handle_event(sid: str, msg: Dict) -> None:
                args = msg.get('args') 
                uuid = msg.get('uuid') 
                response = self.listner(uuid, args)
                return response
                
            
        @self.sio.on('pointerevent')
        def handle_pointerevent(sid: str, msg: dict):
            event = msg.get('msg')
            data = MouseEvent(**event)
            print(data)
        
        @self.sio.on('request_data')
        async def handle_request_data1(sid: str):
          
      
            async def generate_data():
                
                while True:
                    now = datetime.datetime.now()
                    serialized_now = now.isoformat()
                    x = now.timestamp()
                    y1 = math.sin(x)
                    y2 = math.cos(x)  
                    dat = y1/y2# Sinus-artige Daten
                    data_entry = {'Date': y1, 'scales': dat}
                    await self.sio.emit('new_data', data_entry, room=sid)  # Send data to the client
                    yield data_entry
                    await asyncio.sleep(2)
                    # Delay between sending data points

            data_generator = generate_data()

            try:
                async for _ in data_generator:
                    pass
            except KeyboardInterrupt:
                print("\nDatengenerierung wurde gestoppt.")


        
    def read_data_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return "Datei nicht gefunden"
        
        

    def run(self):
        # Starten Sie den Uvicorn-Server in einem separaten Thread
        server_thread = threading.Thread(target=self._start_server)
        server_thread.start()

        # Öffnen Sie den Webbrowser zum angegebenen Host und Port
        url = f"http://{self.host}:{self.port}"
        """ BrowserModule.browser_open(
            native_view=self.native_view, 
            url=url, 
            width=800, 
            height=600, 
            confirm_close=True, 
            port= self.port,
            host=self.host, 
            reload= self.reload, 
            fullscreen=self.fullscreen,
            scrolling=self.scrolling
        )  """
        #url = f"http://{self.host}:{self.port}"
        """ FlaskUI(
        app=self.app_settings,
        socketio=globals.sio,
        server="fastapi",
        width=800,
        height=600
        
        ).run() """
        webbrowser.open(url=url)

    def split_args(self, args: str) -> List[str]:
        return [a.strip() for a in args.split(',')]


    def _start_server(self):
        # Konfigurieren und starten Sie den Uvicorn-Server
        """ config = Config(
            self.app_settings,
            host=self.host,
            port=self.port,
            reload=self.reload,
            reload_includes=self.split_args(self.uvicorn_reload_includes) if self.reload else None,
            reload_excludes=self.split_args(self.uvicorn_reload_excludes) if self.reload else None,
            reload_dirs=self.split_args(self.uvicorn_reload_dirs) if self.reload else None,
            log_level=self.uvicorn_logging_level,
        )
        config.storage_secret = self.storage_secret
        Server(config)
        server = Server(config)
        server.run() """
        uvicorn.run(
            app=self.app_settings, 
            port= self.port, 
            host=self.host, 
            log_level=self.uvicorn_logging_level, 
            reload_dirs=self.split_args(self.uvicorn_reload_dirs) if self.reload else None
            )



if __name__ == "__main__":
    ui = UI()
    ui.run()


