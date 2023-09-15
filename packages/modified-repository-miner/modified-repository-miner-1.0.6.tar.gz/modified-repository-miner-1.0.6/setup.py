#!/usr/bin/env python

from setuptools import setup, find_packages

with open("requirements.txt", "r") as reqs_file:
    requirements = reqs_file.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '1.0.6'

setup(name='modified-repository-miner',
      version=VERSION,
      description='A tool to mine software repositories for defect prediction.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Gerardo Brescia',
      maintainer='Gerardo Brescia',
      author_email='gerrybrescia99@gmail.com',
      url='https://github.com/GerardoBrescia/radon-modified-miner',
      license='Apache License',
      package_dir={'repominer': 'repominer'},
      packages=find_packages(exclude=('tests',)),
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
          "Operating System :: POSIX :: Linux"
      ],
      install_requires=requirements
)
