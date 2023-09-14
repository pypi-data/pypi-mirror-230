#!/usr/bin/env python
"""Script to install nijtaio."""
from distutils.core import setup

setup(name='nijtaio',
      version='1.1',
      packages=['nijtaio'],
      install_requires=['requests', 'soundfile', 'librosa', 'datasets', ],
      entry_points={
        "console_scripts": [
            "voiceharbor = nijtaio.cli:main",
        ],
    },
)
