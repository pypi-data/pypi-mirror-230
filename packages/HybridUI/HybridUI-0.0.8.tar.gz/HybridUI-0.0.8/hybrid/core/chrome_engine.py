import os
import subprocess as subsystem
import sys
from typing import List, Optional
import platform
import webbrowser
OptionsDictT = dict[str, any]

class BrowserModule:
    name: str = 'Google Chrome/Chromium'
    
    @staticmethod
    def run(path: str, options: dict, start_urls: List[str], window_size: Optional[List[int]] = None) -> None:
        if not isinstance(options['cmdline_args'], list):
            raise TypeError("'cmdline_args' option must be of type List[str]")
        if options['app_mode']:
            for url in start_urls:
                subsystem.Popen([path, '--app=%s' % url] +
                        options['cmdline_args'],
                        stdout=subsystem.PIPE, stderr=subsystem.PIPE, stdin=subsystem.PIPE)
                        
        
   
        else:
            args: List[str] = options['cmdline_args'] + start_urls
            if window_size is not None:
                args += ['--window-size=%s,%s' % (window_size[0], window_size[1])]
            subsystem.Popen([path, '--new-window'] + args,
                    stdout=subsystem.PIPE, stderr=sys.stderr, stdin=subsystem.PIPE)
            
    @staticmethod
    def find_path() -> Optional[str]:
        if sys.platform in ['win32', 'win64']:
            return BrowserModule._find_chrome_win()
        elif sys.platform == 'darwin':
            return BrowserModule._find_chrome_mac() or BrowserModule._find_chromium_mac()
        elif sys.platform.startswith('linux'):
            return BrowserModule._find_chrome_linux()
        else:
            return None

    @staticmethod
    def _find_chrome_mac() -> Optional[str]:
        default_dir = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        if os.path.exists(default_dir):
            return default_dir
        # use mdfind ci to locate Chrome in alternate locations and return the first one
        name = 'Google Chrome.app'
        alternate_dirs = [x for x in subsystem.check_output(["mdfind", name]).decode().split('\n') if x.endswith(name)]
        if len(alternate_dirs):
            return alternate_dirs[0] + '/Contents/MacOS/Google Chrome'
        return None

    @staticmethod
    def _find_chromium_mac() -> Optional[str]:
        default_dir = r'/Applications/Chromium.app/Contents/MacOS/Chromium'
        if os.path.exists(default_dir):
            return default_dir
        # use mdfind ci to locate Chromium in alternate locations and return the first one
        name = 'Chromium.app'
        alternate_dirs = [x for x in subsystem.check_output(["mdfind", name]).decode().split('\n') if x.endswith(name)]
        if len(alternate_dirs):
            return alternate_dirs[0] + '/Contents/MacOS/Chromium'
        return None

    @staticmethod
    def _find_chrome_linux() -> Optional[str]:
        import hybrid.core.context as wch
        chrome_names = ['chromium-browser',
                        'chromium',
                        'google-chrome',
                        'google-chrome-stable']

        for name in chrome_names:
            chrome = wch.which(name)
            if chrome is not None:
                return chrome # type: ignore # whichcraft doesn't currently have type hints
        return None

    @staticmethod
    def _find_chrome_win() -> Optional[str]:
        import winreg as reg
        reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
        chrome_path: Optional[str] = None

        for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
            try:
                reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
                chrome_path = reg.QueryValue(reg_key, None)
                reg_key.Close()
                if not os.path.isfile(chrome_path):
                    continue
            except Exception:
                chrome_path = None
            else:
                break

        return chrome_path
    

    # @staticmethod
    # def browser_open(
    #     url: Optional[str] = None,
    #     view: Optional[str]=None,
    #     width: int = None,
    #     height: int = None,
    #     fullscreen: bool = None,
    #     confirm_close: bool =  None
    #     ):
    #     if view =='app':
    #         reload = False
    #         browser_path = BrowserModule.find_path()
    #         parameters = "web"
    #         title = title
    #         flags = [
    #             f"--user-data-dir={parameters}",
    #             "--no-first-run",
    #             "--warn-on-close",
    #             f"--app-name={title}"
    #             ]
    #         if width and height:
    #             flags.extend([f"--window-size={width},{height}"])
    #             options = {'cmdline_args': flags, 'app_mode': True}
    #         if fullscreen == True:
    #             flags.extend(["--start-maximized", '--kiosk'])
    #             options = {'cmdline_args': flags, 'app_mode': True}

    #         if confirm_close == True:
    #             flags.extend(["--warn-on-close"])
    #             options = {'cmdline_args': flags, 'app_mode': True}

    #         if browser_path is not None:
                    
    #             BrowserModule.run(browser_path, options, [url])
    @staticmethod
    def browser_open(
        title: str = None,
        url: Optional[str] = None,
        native_view: Optional[bool]=None,
        width: int = None,
        height: int = None,
        fullscreen: bool = None,
        scrolling:bool= None,
        show_app_icon: bool = True,
        host:str =None,
        port: int = None,
        reload: bool = False,
    ):
        if native_view ==True:
            reload = reload
            browser_path = BrowserModule.find_path()
           
            flags = [
                '--disable-http-cache',
                "--no-first-run",
                f"--app-name={title}"
                ]
            if width and height:
                flags.extend([f"--window-size={width},{height}"])
                options = {'cmdline_args': flags, 'app_mode': True}


            if fullscreen == True:
                flags.extend(["--start-maximized", '--kiosk'])
                options = {'cmdline_args': flags, 'app_mode': True}



            if scrolling == True:
                flags.extend(["Smooth-Scrolling", 'Enabled'])
                options = {'cmdline_args': flags, 'app_mode': True}


            else:
                flags.extend(["Smooth-Scrolling", 'Disabled'])
                options = {'cmdline_args': flags, 'app_mode': True}


            if show_app_icon == True:
                flags.extend(["Smooth---Web-App-Manifest-Icons", 'Enabled'])
                options = {'cmdline_args': flags, 'app_mode': True}
            else:
                flags.extend(["--Web-App-Manifest-Icons", 'Disabled'])
                options = {'cmdline_args': flags, 'app_mode': True}
    

            if browser_path is not None:
                    
                BrowserModule.run(browser_path, options, [url])
        else:
            
            webbrowser.open(f'http://{host if host != "0.0.0.0" else "127.0.0.1"}:{port}/')
        







# # Öffne den Browser im Standardmodus mit der angegebenen URL
# BrowserModule.browser_open(url='https://example.com')

# # Öffne den Browser im Vollbildmodus
# BrowserModule.browser_open(url='https://example.com', fullscreen=True)

# # Öffne den Browser im App-Modus mit angegebener Größe und bestätige das Schließen
# BrowserModule.browser_open(view='app', url='https://example.com', width=800, height=600, confirm_close=True)