#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

from importlib.metadata import entry_points

setup(
    name='nasops',
    version='0.1.2',
    author='yifei.gao, wangyang.zuo',
    author_email='yifei.gao@sophgo.com, wangyang.zuo@sophon.com',
    description='download_from_nas',
    packages=['dtools'],
    entry_points={ 'console_scripts': ['dtools = dtools.main:main'] },
    scripts=['dtools/util.py', 'dtools/main.py'],
    install_requires=["requests","tqdm", "configparser"]
)