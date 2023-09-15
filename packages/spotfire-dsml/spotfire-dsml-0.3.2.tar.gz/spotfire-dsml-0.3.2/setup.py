# Copyright © 2023. Cloud Software Group, Inc.
# This file is subject to the license terms contained
# in the license file that is distributed with this file.

from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with open("LIB_DESCRIPTION.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.3.2'
DESCRIPTION = 'Toolkit for data science and machine learning built by Spotfire'

REQUIREMENTS = [
    'pandas==2.0.3',
    'scikit-learn==1.3.0',
    'tensorflow==2.13.0',
    'numpy==1.24.3',
    'fastapi==0.85.0',
    'uvicorn==0.18.3',
    'category_encoders==2.5.0',
    'matplotlib==3.7.2',
    'seaborn==0.12.2',
    'scikeras==0.11.0',
    'xgboost==1.7.6',
    'cloudpickle==2.2.1',
    'mlxtend==0.21.0',
    'supersmoother==0.4',
    'statsmodels==0.14.0',
    'nltk==3.8.1',
]

DEV_REQUIREMENTS = [
    'pytest==7.1.3',
    'pytest-cov==4.0.0',
    'pylint==2.15.3',
    'black==22.8.0',
    'mypy==0.982',
    'fire==0.4.0',
]

setup(
    name='spotfire-dsml',
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/tibco/dsml-data-functions',
    maintainer='Spotfire Python Package Support',
    maintainer_email='spotfirepython@tibco.com',
    license='BSD License (BSD 3-Clause License)',
    packages=find_packages(
        exclude=[
            'spotfire_dsml.modelling',
            'spotfire_dsml.exploration',
            'spotfire_dsml.module_template',
            'spotfire_dsml.utility'
        ]
    ),
    package_data={
        'PROJECT_NAME_URL': [
            'py.typed',
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'PROJECT_NAME_URL=project_name.my_module:main',
        ]
    },
    python_requires='>=3.8, <4',
)