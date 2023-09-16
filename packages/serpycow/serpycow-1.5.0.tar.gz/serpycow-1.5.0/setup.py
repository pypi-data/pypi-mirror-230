from setuptools import Extension, find_packages, setup

requires = [
    "python-dateutil",
    "python-rapidjson>=0.8.0",
    "typing-inspect>=0.6.0",
    "dataclasses;python_version<'3.7'",
]

with open("README.rst") as f:
    readme = f.read()

setup(
    name="serpycow",
    version="1.5.0",
    description="Fast serialization of dataclasses using Cython",
    long_description=readme,
    author="Sébastien Grignard",
    author_email="pub@amakaze.org",
    url="https://github.com/7ws/serpyco",
    packages=find_packages(),
    package_data={"serpyco": ["*.pyi", "py.typed"]},
    include_package_data=True,
    python_requires=">=3.7",
    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        "setuptools>=18.0",
        "cython<3",
        "pytest-runner",
        "setuptools_scm",
        "wheel",
    ],
    install_requires=requires,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
    ext_modules=[
        Extension("serpyco.serializer", sources=["serpyco/serializer.pyx"]),
        Extension("serpyco.encoder", sources=["serpyco/encoder.pyx"]),
    ],
    zip_safe=False,
)
