#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '1.0.2'

setup(name='terraformmetrics',
      version=VERSION,
      description='A module to extract metrics from Terrafor, scripts',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Gerardo Brescia',
      maintainer='Gerardo Brescia',
      author_email='gerrybrescia99@gmail.com',
      url='https://github.com/GerardoBrescia/radon-terraform-metrics.git',
      download_url=f'https://github.com/radon-h2020/radon-ansible-metrics/archive/{VERSION}.tar.gz',
      packages=find_packages(exclude=('test',)),
      entry_points = {
        'console_scripts': ['terraform-metrics=terraformmetrics.command_line:cli'],
      },
      python_requires='>=3.6',
      classifiers=[
         "Development Status :: 5 - Production/Stable",
         "Intended Audience :: Developers",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
         "Programming Language :: Python :: 3.8",
         "Programming Language :: Python :: 3.9",
         "License :: OSI Approved :: Apache Software License",
         "Topic :: Software Development :: Libraries :: Python Modules",
         "Operating System :: OS Independent"
      ],
      install_requires=[
        'python-hcl2==4.3.2'
      ],
      test_requirements=[
        'pytest==5.4.2'
      ]
)
