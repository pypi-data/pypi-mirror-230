# -*- coding: utf-8 -*-

from setuptools import Extension, setup

__version__ = "1.3.0"

setup(
    ext_modules=[
        Extension("serpyco.serializer", sources=["serpyco/serializer.pyx"]),
        Extension("serpyco.encoder", sources=["serpyco/encoder.pyx"]),
    ],
)
