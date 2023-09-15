from setuptools import setup, Extension
import glob
import numpy
import platform

cppStandard = '/std:c++latest' if platform.system() == 'Windows' else '-std=c++23'

superpositeur = Extension('superpositeur',
                    language='c++',
                    include_dirs = ['include/', numpy.get_include()],
                    sources = glob.glob("src/**/*.cpp") + ["python/PythonAPI.cpp"],
                    extra_compile_args=[cppStandard, "-fomit-frame-pointer", "-flto", "-march=native"],
                )

setup(name = 'superpositeur',
       version = '0.1.0',
       description = 'Superpositeur is a density matrix simulator for quantum operations',
       author = 'Pablo Le Henaff',
       author_email = 'p.lehenaff@tudelft.nl',
       ext_modules = [superpositeur],
       classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
       ],)
