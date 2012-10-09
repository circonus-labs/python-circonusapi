#!/usr/bin/env python
from distutils.core import setup

setup (
    name="circonusapi",
    version="0.1.2",
    description="Circonus API library",
    author="Mark Harrison",
    author_email="mark@omniti.com",
    url="http://github.com/omniti-labs/circonusapi",
    license="ISC",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring"
    ],
    packages=['circonusapi']
)
