import streamlit as st
import base64
from streamlit.components.v1 import html

def render_svg(svg_string):
    """Renders the given svg string."""
    c = st.container()
    with c:
        html(svg_string)

render_svg(open("default.svg").read())