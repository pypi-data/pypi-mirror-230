from setuptools import Extension, setup
from Cython.Build import cythonize


compiler_directives = {"language_level": 3, "embedsignature": True}
extensions = [
    Extension("serpyco.serializer", sources=["serpyco/serializer.pyx"]),
    Extension("serpyco.encoder", sources=["serpyco/encoder.pyx"]),
]
extensions = cythonize(extensions, compiler_directives=compiler_directives)

setup(
    ext_modules=extensions,
)
