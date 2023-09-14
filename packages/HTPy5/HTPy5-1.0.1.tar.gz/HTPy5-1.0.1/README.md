# __HTPy5__

**HTPy5** is a python module used to make static html webpages using python syntax

## Functions

### setup()

A function used to setup the first things at the webpage and they are the `Language`, `Title`, `Description`, `viewport` and `charset`, and the user can't make the webpage without adding the setup code but he can just write it without adding something but it will set all properties to defult.

### addLinking()

A function used to link a file with the html code, returns a string like that.
```html
<link rel="{type of the linking}" herf="linkedFile">
```

### addMeta()

A function used to add a custom meta (as name and content only),returns a string like that :
```html
<meta name="{your meta name}" content="your meta content">
```

### addCustomMeta()

A function used to add a custom meta (as you want),returns like that :
```html
<meta {your attributes}>
```

### addNewHeadElement()

A function used to make anew two sides element like `<element></element>`.

### addNewBodyElement()

A function used to add an element to the body,but with another module at HtPy5 named `Webgets`and can return with one side element or two sides element.


### generateHTML()

This is the most important function,and its used to generate the html after adding elements and returns it as string.

## Add-In-1.0.1 functions

### addNote()

A function used to add a note to the body as the same way of adding a normal element.

### addHeadNote()

A function used to add a note to the head as the same way of adding a normal element.

## addStyle()

A function uses the tool `Stylor` to add styles for the webpage.