# -*- coding: utf-8 -*-
import io
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    regex = r"""__version__\s+=\s+(?P<quote>['"])(?P<version>.+?)(?P=quote)"""
    fp = io.open('aiocassandra.py', mode='rt', encoding='utf-8')
    try:
        return re.search(regex, fp.read()).group('version')
    finally:
        fp.close()


def get_long_description():
    fp = io.open('README.rst', mode='rt', encoding='utf-8')
    try:
        return fp.read()
    finally:
        fp.close()


setup(
    name='aiocassandra',
    version=get_version(),
    author='wikibusiness',
    author_email='osf@wikibusiness.org',
    url='https://github.com/wikibusiness/aiocassandra',
    description='Simple threaded cassandra wrapper for asyncio',
    long_description=get_long_description(),
    install_requires=['cassandra-driver'],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
        ':python_version<="3.2"': ['trollius'],
    },
    py_modules=['aiocassandra'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
