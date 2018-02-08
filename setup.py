# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    regex = r"__version__\s=\s\'(?P<version>[\d\.ab]+?)\'"

    path = 'aiocassandra.py'

    return re.search(regex, read(path)).group('version')


def read(*parts):
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)

    with io.open(filename, encoding='utf-8', mode='rt') as fp:
        return fp.read()


setup(
    name='aiocassandra',
    version=get_version(),
    author='Victor Kovtun',
    author_email='hellysmile@gmail.com',
    url='https://github.com/aio-libs/aiocassandra',
    description='Simple threaded cassandra wrapper for asyncio',
    long_description=read('README.rst'),
    install_requires=['cassandra-driver'],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
        ':python_version=="2.7"': ['trollius'],
    },
    py_modules=[str('aiocassandra')],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords=['cassandra', 'asyncio'],
)
