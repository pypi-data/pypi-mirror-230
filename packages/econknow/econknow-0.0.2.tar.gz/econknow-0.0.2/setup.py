# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 18:07:05 2022
@author:
Зайцева Дарья
"""

from setuptools import setup, find_packages
long_description = '''Library for the 6 semester'''
setup(name='econknow',
      version='0.0.02',
      url='https://github.com/dashkazaitseva',
      packages=['econknow'],
      license='MIT',
      description='',
      zip_safe=False,
      package_data={'econknow': ['*.txt', '*.docx']},
      include_package_data=True
      )