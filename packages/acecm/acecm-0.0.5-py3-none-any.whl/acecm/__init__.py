import os
import streamlit as st
import streamlit.components.v1 as components


parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "build/lib/acecm")

acecm = components.declare_component(
    "acecm",
    path=build_dir
)

def sc(name, value, exp_days, comp_key=None):
    js_ex = f'setCookie(\'{name}\', \'{value}\', {exp_days})'
    if comp_key is None: comp_key=js_ex
    return acecm(js_expressions=js_ex, key=comp_key)

def gc(name, comp_key=None):
    if comp_key is None: comp_key=f'getCookie_{name}'
    return acecm(js_expressions=f'getCookie(\'{name}\')', key=comp_key)

