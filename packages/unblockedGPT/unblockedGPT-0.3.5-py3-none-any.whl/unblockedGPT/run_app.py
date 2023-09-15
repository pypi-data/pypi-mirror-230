import os
import streamlit as st

def run():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(dir_path, 'app.py')
    os.system(f"streamlit run {app_path}")
