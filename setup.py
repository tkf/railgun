from setuptools import setup, find_packages
import numpy
from numpy.distutils.core import Extension

setup(
    name='railgun',
    version="0.1.9.dev3",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description=('ctypes utilities for faster and easier '
                 'simulation programming in C and Python'),
    long_description=open("README.rst").read(),
    author="Takafumi Arakaki",
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/railgun',
    keywords='numerical simulation, research, ctypes, numpy, c',
    license="MIT License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        ],
    include_dirs=[numpy.get_include()],
    ext_modules=[
        Extension(
            'railgun.cstyle',
            sources=['src/cstylemodule.c'],
            extra_compile_args=["-fPIC", "-Wall"],
            ),
        ],
    install_requires=[
        'numpy',
        'six',
    ],
    )
