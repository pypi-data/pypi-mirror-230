from setuptools import setup, find_packages

setup(
    name='pyaudiotoolbox',
    version='0.11',
    author='Abiodun Sulaiman',
    author_email='hello@abiodun.dev',
    description='PyAudioToolBox is a python toolbox for basic audio editing and manipulations',
    long_description='The PyAudioToolBox library provides a set of functions for basic audio editing operations and audio manipulation.',
    packages=find_packages(),
    install_requires=[
        'pydub',
        'moviepy'
    ],
)
