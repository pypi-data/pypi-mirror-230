import os
import subprocess

def run():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(dir_path, 'app.py')
    subprocess.call(['streamlit', 'run', app_path])
