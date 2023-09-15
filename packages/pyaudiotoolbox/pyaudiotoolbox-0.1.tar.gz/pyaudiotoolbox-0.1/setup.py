from setuptools import setup, find_packages

setup(
    name='pyaudiotoolbox',
    version='0.1',
    author='Abiodun Sulaiman',
    author_email='hello@abiodun.dev',
    description='Toolbox for basic audio editing and manipulations',
    packages=find_packages(),
    install_requires=[
        'pydub',
        'moviepy'
    ],
)
