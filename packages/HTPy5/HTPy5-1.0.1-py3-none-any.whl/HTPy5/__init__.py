"""# HtPy5\n
| is a module made to make the website making more better with python,that is an experiment version
\n
Here is a simple example :\n
```python
from HTPy5 import WeBBuild
from HTPy5.Webgets import Widgets
from HTPy5.Htools import Stylor
    
builder = WeBBuild()
builder.setup(title="My WebPage",
              lang="en",
              description="That is my webpage")
    
builder.addLinking(LinkFileName="style.css", LinkType="stylesheet")
builder.addLinking(LinkFileName="responsive.css", LinkType="stylesheet")
builder.addLinking(LinkFileName="print.css", LinkType="stylesheet")
    
builder.addMeta("author", "BoodyWin Workshop")
builder.addMeta("keywords", "python, web development, meta tags")
    
builder.addNewBodyElement(Widgets.button("that is a button"))
builder.addNewBodyElement(Widgets.p("That is some text"))
builder.addNote("That is a note")
builder.addHeadNote("That is a head note")

style = Stylor.Stylor()

style.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.WIDTH,"150px")

style.addStyleCode(["p"],Stylor.SP.CSSProperties.PADDING,"10px")

style_media = style.Media(Stylor.SP.MediaTypes.SCREEN,Stylor.SP.MediaFeatures.PREFERS_COLOR_SCHEME,"dark")
style_media.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.BACKGROUND_COLOR,"black")
style_media.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.COLOR,"white")

style.addMedia(style_media.finalMediaCode())

builder.addStyle(style.finalStyleCode("stylee.css"))
builder.addStyle(style.finalStyleCode())
    
if __name__ == "__main__":
    html = builder.generateHTML()
    with open("index.html","w") as f:
        f.write(html)
    
```
Copyright(c) 2023 by BoodyWin Workshop


Note : Some notes is AI generated.
"""
#                                                                        
#   ███      ███  █████████████████  ██████████     ███          ███     ███████████   
#   ███      ███         ███         ███      ███     ███       ███      ███           
#   ███      ███         ███         ███      ███      ███     ███       ███           
#   ███      ███         ███         ███      ███       ███   ███        ███           
#   ████████████         ███         ██████████           ██ ██          ██████████     
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███           ██████████     
#                                                                                                                                                                                                                       
#                                                                                                                                           
#                                    ██      ██   ████           █████         ████   
#                                    ██      ██     ██          ██   ██          ██   
#                                     ███  ███      ██          ██   ██          ██   
#                                       ████        ██          ██   ██          ██  
#                                        ██       ██████   ██    █████    ██   ██████   
#    
import textwrap

                                                                                                                                   
class SetupError(Exception):
    def __init__(self, message="Cannot generate the HTML without setting up the webpage (or calling `setup()` in the main code)."):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class WeBBuild:
    def __init__(self):
        self.setuped = False
        self.title = ""
        self.lang = ""
        self.description = ""
        self.links = []
        self.charset = "<meta charset=\"UTF-8\">"
        self.viewport = "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
        self.meta_tags = []
        self.elements = []
        self.head_elements = []
        self.css_styles = []

    def setup(self, title="Document", lang="en", viewport=None, charset="UTF-8", description=None):
        self.lang = lang
        self.charset = f"<meta charset=\"{charset}\">"
        self.title = f"<title>{title}</title>"
        if viewport:
            self.viewport = f"<meta name=\"viewport\" content=\"{viewport}\">"
            
        if description:
            self.description = f"<meta name=\"description\" content=\"{description}\">"
        self.setuped = True
        
        

    def addLinking(self, LinkFileName: str, LinkType: str = "stylesheet"):
        """The `addLinking()` method is used to add a link to the webpage.

        Args:
            LinkFileName (str): The href of the link.
            LinkType (str, optional): The type of the link. Defaults to "stylesheet".

        Returns:
            str: The tag of the link.
        """
        link_tag = f"<link rel=\"{LinkType}\" href=\"{LinkFileName}\">"
        self.links.append(link_tag)
        
        return link_tag


    def addMeta(self, MeName: str, MeContent: str):
        """The `addMeta()` method is used to add a meta tag to the webpage.

        Args:
            MeName (str): The name of the meta tag.
            MeContent (str): The content of the meta tag.

        Returns:
            str: The tag of the meta.
        """
        meta_tag = f"<meta name=\"{MeName}\" content=\"{MeContent}\">"
        self.meta_tags.append(meta_tag)
        
        return meta_tag
        
    def addCustomMeta(self,**attributes):
        """The `addCustomMeta()` method is used to add a custom meta tag to the webpage.

        Returns:
            str: The custom meta.
        """
        meta_attr = " ".join([f"{attr}='{val}'" for attr, val in attributes.items()])
        self.meta_tags.append(f"<meta {meta_attr}>")
        
        return f"<meta {meta_attr}>"
        
    def addNewHeadElement(self,Widget):
        """The `addNewHeadElement()` method is used to add a new element to the head of the webpage.

        Args:
            Widget (Webgets): The widget from webgets.

        Returns:
            str: The widget tag.
        """
        self.head_elements.append(Widget)
        return Widget

    def addNewBodyElement(self,Widget):
        """The `addNewBodyElement()` method is used to add a new element to the body of the webpage.

        Args:
            Widget (Webgets): The widget from webgets.

        Returns:
            str: The widget tag.
        """
        self.elements.append(Widget)
        return Widget
    
    def addStyle(self, Style):
        if type(Style) == str:
            css_style = f"""<style>
{Style}
    </style>"""
            self.css_styles.append(css_style)
        elif type(Style) == list:
            link = f"<link rel=\"stylesheet\" href=\"{Style[1]}\">"
            if link in self.links:
                pass
            else:
                self.links.append(link)
            
    def addNote(self,text:str):
        """The `addNote()` method used to add notes the same way to add a normal element.

        Args:
            text (str): The text of the note.

        Returns:
            str: The note code.
        """
        element = f"<!--{text}-->"
        self.elements.append(element)
        return element
    
    def addHeadNote(self,text:str):
        """The `addHeadNote()` method used to add notes the same way to add a normal element but at the webpage head element.

        Args:
            text (str): The text of the note.

        Returns:
            str: The note code.
        """
        element = f"<!--{text}-->"
        self.head_elements.append(element)
        return element
        
    def generateHTML(self):
        if self.setuped:
            all_meta_tags = "\n    ".join(self.meta_tags)
            all_css_links = "\n    ".join(self.links)
            all_elements = "\n    ".join(self.elements)
            all_head_elements = "\n    ".join(self.head_elements)
            all_css_styles = "\n".join(self.css_styles)
            lang_attr = f" lang=\"{self.lang}\"" if self.lang else ""
            html = f"""<!DOCTYPE html>
<html{lang_attr}>
<head>
    {self.title}
    {self.description}
    {self.charset}
    {self.viewport}
    {all_meta_tags}
    {all_head_elements}
    {all_css_styles}
    {all_css_links}
</head>
<body>
    {all_elements}
</body>
</html>"""
            formatted_html = textwrap.dedent(html).strip()
            return formatted_html
        else:
            raise SetupError("Cannot generate the HTML without setting up the webpage (or calling `setup()` in the main code).")

__all__ = ['Webgets','WeBuild',"HtTools"]
__version__ = "1.0.1"
__title__ = "HTPy5"
__author__ = "boodywin_workshop"
__email__ = "boodywin.studio.123@gmail.com"
__copyright__ = """BoodyWin Workshop Python Module License Agreement

Copyright (c) 2023 BoodyWin Workshop

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__license__ = "MIT"

# Example usage:
def main():
    from Webgets import Widgets
    from Htools import Stylor
        
    builder = WeBBuild()
    builder.setup(title="My WebPage",
                lang="en",
                description="That is my webpage")
        
    builder.addLinking(LinkFileName="style.css", LinkType="stylesheet")
    builder.addLinking(LinkFileName="responsive.css", LinkType="stylesheet")
    builder.addLinking(LinkFileName="print.css", LinkType="stylesheet")
        
    builder.addMeta("author", "BoodyWin Workshop")
    builder.addMeta("keywords", "python, web development, meta tags")
        
    builder.addNewBodyElement(Widgets.button("that is a button"))
    builder.addNewBodyElement(Widgets.p("That is some text"))
    builder.addNote("That is a note")
    builder.addHeadNote("That is a head note")

    style = Stylor.Stylor()

    style.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.WIDTH,"150px")

    style.addStyleCode(["p"],Stylor.SP.CSSProperties.PADDING,"10px")

    style_media = style.Media(Stylor.SP.MediaTypes.SCREEN,Stylor.SP.MediaFeatures.PREFERS_COLOR_SCHEME,"dark")
    style_media.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.BACKGROUND_COLOR,"black")
    style_media.addStyleCode(["button","input[type='button']"],Stylor.SP.CSSProperties.COLOR,"white")

    style.addMedia(style_media.finalMediaCode())

    builder.addStyle(style.finalStyleCode("stylee.css"))
    builder.addStyle(style.finalStyleCode())
        
    if __name__ == "__main__":
        html = builder.generateHTML()
        with open("index.html","w") as f:
            f.write(html)

if __name__ == "__main__":
    main()