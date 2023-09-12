#!/usr/bin/python3
# This file is auto generated. Do not modify
from setuptools import setup
setup(
    name='typedload',
    version='2.26',
    description='Load and dump data from json-like format into typed data structures',
    readme='README.md',
    url='https://ltworf.github.io/typedload/',
    author="Salvo 'LtWorf' Tomaselli",
    author_email='tiposchi@tiscali.it',
    license='GPL-3.0-only',
    classifiers=['Development Status :: 5 - Production/Stable', 'Intended Audience :: Developers', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Typing :: Typed', 'Programming Language :: Python :: 3.8', 'Programming Language :: Python :: 3.9', 'Programming Language :: Python :: 3.10', 'Programming Language :: Python :: 3.11', 'Programming Language :: Python :: 3.12'],
    keywords='typing types mypy json schema json-schema python3 namedtuple enums dataclass pydantic',
    packages=['typedload'],
    package_data={"typedload": ["py.typed", "__init__.pyi"]},
)
