from setuptools import Extension, setup
from Cython.Build import build_ext, cythonize


extensions = [
    Extension("serpyco.serializer", sources=["serpyco/serializer.pyx"]),
    Extension("serpyco.encoder", sources=["serpyco/encoder.pyx"]),
]
extensions = cythonize(extensions)

setup(
    ext_modules=extensions,
    cmdclass={'build_ext': build_ext},
)
