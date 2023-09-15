from setuptools import setup, find_packages

setup(
    name='unblockedGPT',
    version='0.3.3',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'requests',
        'openai',
        'pycryptodome',  # This provides the Crypto module
    ],
    entry_points={
        'console_scripts': [
            'unblockedGPT = unblockedGPT.run_app:run',
        ],
    },
)

def run():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(dir_path, 'app.py')
    st.command(f"streamlit run {app_path}")


