__author__ = 'Alex Rogozhnikov'

from setuptools import setup

setup(
    name="newpyter",
    version='0.5.2',
    packages=['newpyter', 'newpyter.storage', 'newpyter.newpyviewer'],
    install_requires=[
        # useful for grammars
        'parsimonious',
        'nbformat',
        'sh',
        # download / upload to aws
        'boto3',
        # to parse configuration
        'toml',
        # for exception types, but it should be installed by jupyter
        'tornado',
    ],
    extras_require={
        'viewer': ["fastapi~=0.85.1", "nbconvert~=7.2.2"]
    },
    entry_points={
        'console_scripts': [
            'newpyter=newpyter.__main__:main',
        ]
    },
)