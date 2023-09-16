import setuptools
from Cython.Build import cythonize

setuptools.setup(
    ext_modules = cythonize("qocttools/cythonfuncs.pyx", language_level = 3)
)

