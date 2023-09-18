#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   setup.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Setup module
'''

import re
import setuptools

# read the contents of your README file
with open("README.md", "r", encoding="utf8") as rd:
    long_description = rd.read()

# read the version number
with open('datature/__init__.py', "r", encoding="utf8") as rd:
    version = re.search(r'SDK_VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        rd.read()).group(1)

setuptools.setup(
    name="datature",
    version=version,
    author="Raighne Weng",
    author_email="raighne@datature.io",
    long_description_content_type="text/markdown",
    long_description=long_description,
    project_urls={
        "Homepage": "https://www.datature.io/",
        "Documentation": "https://developers.datature.io/docs/python-sdk"
    },
    description="Python bindings for the Datature API",
    packages=setuptools.find_namespace_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests==2.28.1", "google-crc32c==1.5.0", "pyhumps==3.8.0", "pyyaml==6.0",
        "inquirer>=2.10.1", "halo==0.0.31", "filetype==1.2.0", "opencv-python==4.7.0.72",
        "alive-progress==3.0.1", "pydicom==2.3.1", "nibabel>=4.0.2", "matplotlib>=3.5.3"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License"
    ],
    extras_require={
        'docs': ["sphinx", "sphinx-rtd-theme", "sphinx_markdown_builder"]
    },
    entry_points={
        'console_scripts': ['datature=datature.cli.main:main'],
    },
)
