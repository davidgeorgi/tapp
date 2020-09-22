#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "numpy==1.18.5",
    "pandas==1.0.5",
    "nltk==3.5",
    "scikit-learn==0.23.1",
    "setuptools==49.2.0",
    "tensorflow==2.3.0",
    "pm4py==1.5.1",
    "gensim==3.8.3"
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="David Georgi",
    author_email='david.georgi@rwth-aachen.de',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    description="Text-Aware Process Prediction Model",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tapp',
    name='tapp',
    packages=find_packages(include=['tapp', 'tapp.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/davidgeorgi/tapp',
    version='0.1',
    zip_safe=False,
)
