# -*- coding: utf-8 -*-
'''
WebChat: An anonymous chatting room service
'''

from setuptools import setup

from webchat.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "webchat",
    version = __version__,
    description = "webchat",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/fiefdx/WebChat",
    author = "fiefdx",
    author_email = "fiefdx@163.com",
    packages = [
        'webchat',
        'webchat.handlers',
        'webchat.utils',
        'webchat.modules',
    ],
    entry_points = {
        'console_scripts': [
            'webchat = webchat.chat:main',
        ],
    },
    install_requires = [
        "tornado",
        "pyYAML",
    ],
    include_package_data = True,
    license = "MIT",
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ]
)
