# python setup.py build_ext --inplace
import os
from sys import platform
print("Found platform:", platform)

from setuptools import find_packages
from setuptools import setup, Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext as _build_ext

import numpy as np




print(find_packages())


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        try:
            __builtins__.__NUMPY_SETUP__ = False
        except AttributeError as e:
            pass
        import numpy as np
        self.include_dirs.append(np.get_include())


setup(
    name='libttp',
    version='0.1.42',
    url='https://github.com/VicidominiLab/libttp',
    license='CC-BY-NC-4.0',
    author='Mattia Donato',
    author_email='mattia.donato@iit.it',
    description='Libraries for reading the data from time-tagging module (BrightEyes-TTM, https://github.com/VicidominiLab/BrightEyes-TTM)',
    ext_modules=cythonize("libttp/ttpCython.pyx", compiler_directives={'language_level' : "3"}, include_path=[np.get_include()]),
    packages=find_packages(),
    install_requires=['cython>=0.29.30', 'numpy>=1.22.0', 'matplotlib', 'pandas', 'tdqm', 'scipy'],
    include_dir=[np.get_include()],
    include_dirs=[np.get_include()],
    setup_requires=['cython>=0.29.30', 'numpy>=1.22.0'],
    cmdclass={'build_ext': build_ext},
)

