# -*- coding: utf-8 -*-
"""
@author: enfantbenidedieu
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scientistmetrics", 
    version="0.0.3",
    author="Duverier DJIFACK ZEBAZE",
    author_email="duverierdjifack@gmail.com",
    description="Python package for metrics and scoring : quantifying the quality of predictions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enfantbenidedieu/scientistmetrics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)