# Hybrid foundation 

<img src="https://github.com/AriBermeki/logo/blob/main/logo%20(5).png" width="100%"/>
<p align="center">
  <a href="https://ant.design">
    <img width="100" src="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg">
  </a>
</p>

<h3 align="center">Hybrid with Ant Design UI</h1>

<p align="center">Create an efficient and enjoyable work experience</p>

![](https://gw.alipayobjects.com/mdn/rms_08e378/afts/img/A*zx7LTI_ECSAAAAAAAAAAAABkARQnAQ)
<p>Hybrid empowers developers to effortlessly build real-time web, mobile, and desktop applications in Python, without requiring prior frontend experience.</p>
<p>It is an incredibly powerful Python library that allows you to create cross-platform graphical user interface and Web applications with ease, similar to Electronjs, but with an integrated React  and Ant Design user interface.</p>



## ⚡ From idea to app in minutes
<p>This feature makes Hybrid an ideal choice for creating sophisticated and comprehensive applications, catering to even the most demanding use cases.</p>
<p>At the heart of Hybrid's architecture are cutting-edge technologies such as React, FastAPI, Chrome, and Uvicorn, providing an excellent platform for building high-quality applications that seamlessly blend into any environment.</p>
<p>Hybrid also supports the Python ZVT 700 electronic cash register interface, allowing for seamless integration of other transactions into your applications. Additionally, Hybrid supports PWA Progressive Web Applications, enabling easy installation of your app on IOS and Android operating systems.</p>




## 🔋 Batteries included
<p>If you're looking for a robust and versatile library to create visually stunning applications, then Hybrid is undoubtedly the right choice. Explore the full potential of this exceptional library by giving it a try today!</p>
<a href="https://badge.fury.io/py/Hybrid"><img src="https://badge.fury.io/py/Hybrid.svg" alt="PyPI version" height="18"></a>
<a href='https://hybrid-document.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/hybrid-document/badge/?version=latest' alt='Documentation Status' />
</a>

## 📐 Simple architecture

No more complex architecture with JavaScript frontend, REST API backend, database, cache, etc. With Hybrid you just write a monolith stateful app in Python only and get multi-user, realtime Single-Page Application (SPA).
## ✨ Features

- browser-based graphical user interface
- standard GUI elements like label, button, checkbox, switch, slider, input, file upload, ...
- simple grouping with rows, columns, cards and dialogs
- general-purpose HTML and Markdown elements
- powerful high-level elements to
  - plot graphs and charts,
  - render 3D scenes,
  - get steering events via virtual joysticks
  - annotate and overlay images
  - interact with tables
  - navigate foldable tree structures
- notifications, dialogs and menus to provide state of the art user interaction
- shared and individual web pages
- ability to add custom routes and data responses
- capture keyboard input for global shortcuts etc.
- customize look by defining primary, secondary and accent colors
- live-cycle events and session data




  ![](https://user-images.githubusercontent.com/507615/209472919-6f7e8561-be8c-4b0b-9976-eb3c692aa20a.png)


## 🖥 Environment Support

- Modern browsers
- Client-side Rendering

## Browsers support

| [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/edge/edge_48x48.png" alt="IE / Edge" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>IE / Edge | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/firefox/firefox_48x48.png" alt="Firefox" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>Firefox | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/chrome/chrome_48x48.png" alt="Chrome" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>Chrome | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari/safari_48x48.png" alt="Safari" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>Safari | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari-ios/safari-ios_48x48.png" alt="iOS Safari" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>iOS Safari | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/samsung-internet/samsung-internet_48x48.png" alt="Samsung" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>Samsung | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/opera/opera_48x48.png" alt="Opera" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)<br/>Opera |
| --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| IE11, Edge| last 2 versions| last 2 versions| last 2 versions| last 2 versions| last 2 versions| last 2 versions 


## 📦 Install

```bash
pip install HybridUI
```
## 🔨 Usage

Write your Hybrid UI:

```python
from hybrid import interface
layout = interface.title(content='Hello World from Hybrid UI!')
app = interface.compiler(layout=layout, globale_ui_style='main.css')
app.run()
 
   
```

```python


from hybrid import interface






if __name__ == '__main__':

    def main(data):
        print(data)

    d1 = interface.title(content='Hybrid with Ant Design UI', level=2)
    d2 = interface.slider(onChange=main)
    image = interface.image(src="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg", alt='hallo', width='350px', height='350px')
    content = interface.content(content=[d1,d2, image])

    app = interface.compiler(layout=content,globale_ui_style='main.css')
    app.run()
 
   
```
<img width="50%" src="https://raw.githubusercontent.com/AriBermeki/logo/main/example.png?token=GHSAT0AAAAAACB7YTQISEN2ZMMLKTWEUH5AZIFUWNA">

```python
from hybrid import interface

# example with Button onclick

def main():
  print('Hallo')


layout = interface.button(text='Click', onclick=main)
app = interface.compiler(layout=layout, globale_ui_style='main.css')
app.run()
 
   
```
<img width="50%" src="https://raw.githubusercontent.com/AriBermeki/logo/main/example1.png?token=GHSAT0AAAAAACB7YTQJY6EVAT2RZGQTG5CUZIFUXLQ">

```python
from hybrid import interface



def main(message):
  print(f'Hallo{message}')


layout = interface.input(placeholder='Click', onchange=main)
app = interface.compiler(layout=layout, globale_ui_style='main.css')
app.run()
 
   
```


<img width="50%" src="https://raw.githubusercontent.com/AriBermeki/logo/main/example2.png?token=GHSAT0AAAAAACB7YTQILUBDQ4WATNLWCYRQZIFUZAA">



```python
from hybrid import interface

# example with violinChart

def main():
  print('Hallo')


layout = interface.violinChart()
app = interface.compiler(layout=layout, globale_ui_style='main.css')
app.run()
 
   
```
<img width="50%" src="https://raw.githubusercontent.com/AriBermeki/logo/main/example4.png?token=GHSAT0AAAAAACB7YTQIDUH4E5XQEIUUWISSZIFU3XA">


```python

from hybrid import interface

# example with slider onchage

def main(message):
  print(f'slider value{message}')


layout = interface.slider(onchange=main)
app = interface.compiler(layout=layout, globale_ui_style='main.css')
app.run()
 
   
```
### In August 2023, Hybrid has just been publicly released by software architecture Ari Bermeki and is in Alpha Stage.
Anyone can install and use Hybrid. There may be issues, but we are actively working to resolve them.


## 🤝 Contributing [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
