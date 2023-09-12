from setuptools import setup
import os

# Carregar o conteúdo do arquivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pydark',
    version='0.0.1',
    description='DarkPy is a Python library which brings some useful calculations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['pydark', 'pydark.date', 'pydark.math', 'pydark.text'],
    install_requires=[],
)
