#!/usr/bin/env python

from os import path
from codecs import open
from setuptools import setup, find_packages

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

requirements = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs if x.startswith('git+')]

setup(
    name="riot_mde",
    version=__version__,
    description="A package for modeling real-time IoT systems",
    url="https://github.com/robotics-4-all/2020_riot_mde_thanos_manolis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author="Athanasios Manolis",
    author_email="thanos.m14@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'riot_mde = riot_mde.parser:main'
        ]
    },
    py_modules=['riot_mde.parser', 'riot_mde.model_2_plantuml', 'riot_mde.hw_conns_plantuml', 'riot_mde.definitions'],
    packages=find_packages(),
    dependency_links=dependency_links,
    python_requires='>=3.6'
)