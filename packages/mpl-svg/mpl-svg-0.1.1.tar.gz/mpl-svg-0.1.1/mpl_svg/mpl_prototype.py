import io
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup

svg_css = "<style>" + open("css/plot_css3.css").read() + "</style>"
st.markdown(svg_css, unsafe_allow_html=True)

value = st.slider("Slider", 0.0, 0.5, 0.01)

x = np.arange(0,100,0.01)
y = 0.5*x*np.sin(value*np.pi*x)
yb = 0.4*x*np.sin(value*np.pi*x)
plt.plot(x, y)
plt.plot(x, yb)
f = io.BytesIO()
plt.savefig(f, format="svg")

svg_string = f.getvalue().decode("utf-8")

svg_soup = BeautifulSoup(f.getvalue(), 'lxml')

svg_element = svg_soup.find("svg")

if 'class' in svg_element.attrs:
    svg_element['class'] = svg_element['class'] + " " + "matplotlib-svg"
else:
    svg_element['class'] = "matplotlib-svg"

## edit svg
all_elements = svg_soup.find_all()

def add_class(element, class_name):
    if 'class' in element.attrs:
        element['class'] = element['class'] + " " + class_name
    else:
        element['class'] = class_name

css_styles = """/* ---------------------------------------------------- */
/* SVG area and plot area */\n
/* Matplotlib SVG */ 
svg.matplotlib-svg {
    width: 100%;
    height: auto;
    margin-bottom: 1rem;
}\n\n"""
for element in all_elements:
    if 'id' in element.attrs:
        add_class(element, element['id'].split("_")[0].replace(".", "-"))
        paths = element.find_all("path")
        for path in paths:
            if path.parent.name != "defs":
                add_class(path, element['id'].split("_")[0].replace(".", "-"))
        
paths = svg_soup.find_all("path")
path_count = 0
css_styles += """/* Matplotlib SVG background */
.figure > .patch:first-child > path {
    fill: #123413;
}\n\n
/* Plot area background */
.figure > .axes > .patch:first-child > path.figure.axes.patch {
    fill: #999999;
}\n\n
/* Plot area border (remove contents if 
you want to style individual sides)*/
.axes > .patch > .figure.axes.patch {
    fill: none;
	stroke: #db1818;
	stroke-width: 0.8;
	stroke-linejoin: miter;
	stroke-linecap: square;
}\n\n
"""
for path in paths:
    if path.parent.name != "defs":
        add_class(path, "path-" + str(path_count))
        if "style" in path.attrs:
            css_styles += '.' + '.'.join(path['class'].split()) + ' {\n\t' +  path['style'].replace('; ', ';\n\t') + ';\n}\n\n'
            path['style'] = ""
        else:
            css_styles += '.' + '.'.join(path['class'].split()) + ' {\n}\n\n'
        path_count += 1

use_count = 0
uses_inside = svg_soup.find_all("use")
css_styles += """/* All axes tickmarks and text */
.copy {
\tfill: white;
\tstroke: white;
\tstroke-width: 1px;
}

/* All x-axes tickmarks and text */
.xtick .copy {
\tfill: green;
\tstroke: green;
\tstroke-width: 3px;
}

/* All x-axes text */
.xtick .text .copy {
\tfill: blue;
\tstroke: blue;
\tstroke-width: 1px;
}

/* All y-axes tickmarks and text */
.ytick .copy {
\tfill: green;
\tstroke: green;
\tstroke-width: 1px;
}

/* All y-axes text */
.ytick .text .copy {
\tfill: red;
}

/* Override all axes tickmarks and text */
.axes .matplotlib-axis .xtick .copy, .axes .matplotlib-axis .ytick .copy {
	fill: #ffffff;
	stroke: #ffffff;
	stroke-width: 2px;
}\n
/* ---------------------------------------------------- */
/* Individual axis elements (ticks and text characters) */
\n"""
for use_element in uses_inside:
    add_class(use_element, "copy copy-" + str(use_count))
    if "style" in use_element.attrs:
        css_styles += '.copy-' + str(use_count) + ' {\n\t' + use_element['style'].replace('; ', ';\n\t') + ';\n}\n\n'
        use_element['style'] = ""
    else:
        css_styles += '.copy-' + str(use_count) + ' {\n}\n\n'
    use_count += 1
      
path_styles_in_defs ="""/* ---------------------------------------------------- */
/* Original paths of copies */\n\n"""
class_count = 0
def_elem_dict = {}
defs_elements = svg_soup.find_all("defs")
for defs in defs_elements:
    elements = defs.find_all()
    for element in elements:
        if 'id' in element.attrs:
            def_elem_dict[element['id']] = element

            if "class" in element.attrs:
                element['class'] = "def-" + element.name + "-" + str(class_count)
                class_count += 1
                if "style" in element.attrs:
                    path_styles_in_defs += '.' + '.'.join(element['class'].split()) + ' {\n\t/*' + element['style'].replace('; ', ';\n\t') + ';*/\n}\n\n'
                    element['style'] = ""
                else:
                    path_styles_in_defs += '.' + '.'.join(element['class'].split()) + ' {\n}\n\n'

st.markdown(svg_soup.prettify(), unsafe_allow_html=True)

st.code(css_styles + path_styles_in_defs, language="css")
