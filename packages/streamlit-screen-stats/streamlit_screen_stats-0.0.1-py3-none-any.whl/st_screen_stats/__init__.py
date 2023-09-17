import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _st_screen_data = components.declare_component(

        "st_screen_data",

        url="http://localhost:3001",
    )
else:
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _st_screen_data = components.declare_component("st_screen_data", path=build_dir)


def st_screen_data(setTime=None, key=None):

    component_value = _st_screen_data(setTime=setTime, key=key, default=0)

    return component_value



