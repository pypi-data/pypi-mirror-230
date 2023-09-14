#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='sweep',
      version='2.0.1.4',
      author='Diogo de J. S. Machado',
      author_email='diogomachado.bioinfo@gmail.com',
      description='SWeeP is a tool for representing large biological sequences datasets in compact vectors',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      long_description_content_type='text/markdown',
      long_description=open('README.md').read(),
      zip_safe=False,
      install_requires=['numpy', 'Biopython', 'scipy', 'tqdm', 'h5py'],
      package_data = {'': ['*.mat']},
      license = 'BSD-3-Clause',
      url='https://github.com/diogomachado-bioinfo/sweep',
      )
