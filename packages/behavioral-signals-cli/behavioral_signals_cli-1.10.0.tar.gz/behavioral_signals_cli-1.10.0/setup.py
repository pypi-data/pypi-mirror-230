# -*- coding: utf-8 -*-

"""Setup script for the Behavioral Signals CLI package."""

from pathlib import Path
from setuptools import setup, find_packages

PACKAGE_NAME = 'behavioral_signals_cli'
VERSION = '1.10.0'

THIS_DIRECTORY = Path(__file__).parent
LONG_DESCRIPTION = (THIS_DIRECTORY / 'README.md').read_text()

REQUIREMENTS = [
    'aiofiles==0.8.0',
    'aiosignal==1.2.0',
    'aiohttp==3.8.5',
    'attrs==22.2.0',
    'async-timeout==4.0.2',
    'behavioral-signals-swagger-client-3==3.11.1',
    'dotmap==1.3.30',
    'tqdm==4.64.1',
    'typing_extensions==4.1.1',
    'ruamel.yaml==0.17.21',
    'requests==2.27.1',
    'ratelimit==2.2.1',
    'yarl==1.7.2',
    'zipp==3.6.0',
]

TEST_REQUIREMENTS = [
    'pytest',
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='Command Line Interface for Behavioral Signals Emotion and '
                'Behavior Recognition Engine in the Cloud',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Behavioral Signals',
    author_email='nassos@behavioralsignals.com',
    url='https://bitbucket.org/behavioralsignals/api-cli/src',
    download_url=f'https://bitbucket.org/behavioralsignals/api-cli/get/{VERSION}.tar.gz',
    packages=find_packages(include=[PACKAGE_NAME]),
    entry_points={
        'console_scripts': [
            f'{PACKAGE_NAME}=behavioral_signals_cli.cmd:main',
            'bsi-cli=behavioral_signals_cli.cmd:main'
        ]
    },
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    license='MIT license',
    zip_safe=False,
    keywords=[
        'behavioral signals',
        'cli',
        'command line interface',
        'emotion recognition',
        'behavior recognition',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
