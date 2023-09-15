from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize

extensions = [
    Extension(
        "timestamp",
        sources=["timestamp.pyx"],
        extra_compile_args=["-O3"],
    )
]
setup(ext_modules=cythonize(extensions))
