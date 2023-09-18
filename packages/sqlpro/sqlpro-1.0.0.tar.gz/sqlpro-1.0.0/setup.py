# coding=utf-8
from setuptools import setup

setup(
    name="sqlpro",
    version="1.0.0",
    description="The simple sqlite3 library supports encrypted files and querying data",
    packages=["sqlitepro"],
    data_files=[('sqlitepro', ['sqlitepro/sqlite3.dll'])],
    long_description="The simple sqlite3 library supports encrypted files and querying dat"
)
