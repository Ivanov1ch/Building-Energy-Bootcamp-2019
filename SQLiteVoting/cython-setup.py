import os
from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize(os.path.join('SQLiteVoting', 'main.py')))
