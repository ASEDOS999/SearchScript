#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:57:08 2020

@author: elias
"""

from setuptools import setup, find_packages
 
setup(name='ScriptExtract',
      version='0.0',
      url='https://github.com/ASEDOS999/SearchScript',
      license='MIT',
      author='Gigi Sayfan',
      author_email='kuruzov.ia@phystech.edu',
      description='Script Extractions',
      packages=find_packages(exclude=['ScriptExtract']),
      include_package_data = True,
      long_description=open('README.md').read(),
      zip_safe=False)