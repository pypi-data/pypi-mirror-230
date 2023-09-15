from setuptools import setup, find_packages

setup(
    name='unblockedGPT',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'requests',
        'openai',
        'pycryptodome',  # This provides the Crypto module
        'base64'  # Note: base64 is a standard library module, so it's not necessary to list it here
    ],
    entry_points={
        'console_scripts': [
            'chat = unblockedGPT.run_app:run',
        ],
    },
)
