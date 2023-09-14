class Widgets:
    def a(href: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"href=\"{href}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<a {element_attrs}>{Content}</a>"

    def abbr(Title: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"title=\"{Title}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<abbr {element_attrs}>{Content}</abbr>"

    def address(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<address {element_attrs}>{Content}</address>"

    def article(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<article {element_attrs}>{Content}</article>"

    def aside(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<aside {element_attrs}>{Content}</aside>"

    def audio(src: str, controls: bool = True, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"src=\"{src}\""
        element_attrs += f" controls=\"{controls}\"" if controls else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<audio {element_attrs}></audio>"

    def b(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<b {element_attrs}>{Content}</b>"

    def base(href: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"href=\"{href}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<base {element_attrs}>"

    def bdo(dir: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"dir=\"{dir}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<bdo {element_attrs}>{Content}</bdo>"

    def blockquote(cite: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"cite=\"{cite}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<blockquote {element_attrs}>{Content}</blockquote>"

    def body(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<body {element_attrs}>{Content}</body>"

    def br(clear: str = "both", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"clear=\"{clear}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<br {element_attrs}>"

    def button(value: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"type=\"button\""
        element_attrs += f" value=\"{value}\"" if value else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<input {element_attrs}>"

    def canvas(width: str = "100px", height: str = "100px", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"width=\"{width}\""
        element_attrs += f" height=\"{height}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<canvas {element_attrs}></canvas>"

    def caption(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<caption {element_attrs}>{Content}</caption>"

    def cite(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<cite {element_attrs}>{Content}</cite>"

    def code(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<code {element_attrs}>{Content}</code>"

    def col(span: int = 1, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"span=\"{span}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<col {element_attrs}>"

    def colgroup(span: int = 1, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"span=\"{span}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<colgroup {element_attrs}>"

    def dd(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<dd {element_attrs}>{Content}</dd>"

    def deleted(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<del {element_attrs}>{Content}</del>"

    def details(open: bool = False, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"open=\"{open}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<details {element_attrs}>"

    def dfn(term: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"term=\"{term}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<dfn {element_attrs}>{Content}</dfn>"

    def dialog(open: bool = False, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"open=\"{open}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<dialog {element_attrs}>"

    def div(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<div {element_attrs}>{Content}</div>"

    def dl(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<dl {element_attrs}>"

    def fieldset(legend: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"legend=\"{legend}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<fieldset {element_attrs}>{Content}</fieldset>"

    def font(size: str = "16px", color: str = "black", face: str = "sans-serif", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"size=\"{size}\""
        element_attrs += f" color=\"{color}\""
        element_attrs += f" face=\"{face}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<font {element_attrs}>"

    def form(action: str, method: str = "get", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"action=\"{action}\""
        element_attrs += f" method=\"{method}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<form {element_attrs}>"

    def header(level: int, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"level=\"{level}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<header {element_attrs}>{Content}</header>"

    def hr(size: str = "1px", width: str = "100%", align: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"size=\"{size}\""
        element_attrs += f" width=\"{width}\""
        element_attrs += f" align=\"{align}\"" if align else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<hr {element_attrs}>"

    def html(lang: str = "en", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"lang=\"{lang}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<html {element_attrs}>"

    def iframe(src: str, width: str = "300px", height: str = "200px", frameborder: str = "0", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"src=\"{src}\""
        element_attrs += f" width=\"{width}\""
        element_attrs += f" height=\"{height}\""
        element_attrs += f" frameborder=\"{frameborder}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<iframe {element_attrs}>"

    def img(src: str, alt: str = None, width: str = None, height: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"src=\"{src}\""
        element_attrs += f" alt=\"{alt}\"" if alt else ""
        element_attrs += f" width=\"{width}\"" if width else ""
        element_attrs += f" height=\"{height}\"" if height else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<img {element_attrs}>"

    def input(type: str = "text", name: str = None, value: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"type=\"{type}\""
        element_attrs += f" name=\"{name}\"" if name else ""
        element_attrs += f" value=\"{value}\"" if value else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<input {element_attrs}>"

    def label(ForElement: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"for=\"{ForElement}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<label {element_attrs}>{Content}</label>"

    def legend(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<legend {element_attrs}>{Content}</legend>"

    def li(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<li {element_attrs}>{Content}</li>"

    def link(href: str, rel: str = None, type: str = "text/css", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"href=\"{href}\""
        element_attrs += f" rel=\"{rel}\"" if rel else ""
        element_attrs += f" type=\"{type}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<link {element_attrs}>"

    def meta(name: str, content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"name=\"{name}\""
        element_attrs += f" content=\"{content}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<meta {element_attrs}>"

    def meter(value: float, min: float, max: float, low: float = None, high: float = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"value=\"{value}\""
        element_attrs += f" min=\"{min}\""
        element_attrs += f" max=\"{max}\""
        element_attrs += f" low=\"{low}\"" if low else ""
        element_attrs += f" high=\"{high}\"" if high else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<meter {element_attrs}>"

    def nav(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<nav {element_attrs}>"

    def ol(start: int = 1, type: str = "1", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"start=\"{start}\""
        element_attrs += f" type=\"{type}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<ol {element_attrs}>"

    def optgroup(label: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"label=\"{label}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<optgroup {element_attrs}>"

    def option(value: str, selected: bool = False, disabled: bool = False, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"value=\"{value}\""
        element_attrs += f" selected=\"{selected}\"" if selected else ""
        element_attrs += f" disabled=\"{disabled}\"" if disabled else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<option {element_attrs}>"

    def output(ForElement: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"for=\"{ForElement}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<output {element_attrs}>{Content}</output>"

    def p(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<p {element_attrs}>{Content}</p>"

    def param(name: str, value: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"name=\"{name}\""
        element_attrs += f" value=\"{value}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<param {element_attrs}>"

    def progress(value: float, max: float, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"value=\"{value}\""
        element_attrs += f" max=\"{max}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<progress {element_attrs}>"

    def q(cite: str, Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"cite=\"{cite}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<q {element_attrs}>{Content}</q>"

    def reset(value: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"type=\"reset\""
        element_attrs += f" value=\"{value}\"" if value else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<input {element_attrs} value=\"{value}\">"
    
    def section(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<section {element_attrs}>"

    def select(name: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"name=\"{name}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<select {element_attrs}>"

    def source(src: str, type: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"src=\"{src}\""
        element_attrs += f" type=\"{type}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<source {element_attrs}>"

    def submit(value: str = None, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"type=\"submit\""
        element_attrs += f" value=\"{value}\"" if value else ""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<input {element_attrs} value=\"{value}\">"
    
    def table(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<table {element_attrs}>"

    def textarea(name: str, cols: str = "20", rows: str = "10", ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"name=\"{name}\""
        element_attrs += f" cols=\"{cols}\""
        element_attrs += f" rows=\"{rows}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<textarea {element_attrs}>"

    def time(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<time {element_attrs}>"

    def title(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<title {element_attrs}>{Content}</title>"

    def tr(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<tr {element_attrs}>"

    def ul(ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<ul {element_attrs}>"

    def var(name: str, ID: str = None, CLASS: str = None, style: str = None, **attributes):
        element_attrs = f"name=\"{name}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        return f"<var {element_attrs}>"

    def video(src: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = f"src=\"{src}\""
        element_attrs += " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<video {element_attrs}>"

    def wbr(Content: str, ID: str = None, CLASS: str = None, NAME: str = None, style: str = None, **attributes):
        element_attrs = " ".join([f"{attr}=\"{val}\"" for attr, val in attributes.items()])
        element_attrs += f" id=\"{ID}\"" if ID else ""
        element_attrs += f" class=\"{CLASS}\"" if CLASS else ""
        element_attrs += f" name=\"{NAME}\"" if NAME else ""
        return f"<wbr {element_attrs}>{Content}</wbr>"

