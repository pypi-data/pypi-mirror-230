import os
from distutils.core import setup
from setuptools import find_packages


test_deps = ['mock==3.0.5', 'pytest==4.6.4']

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))

VERSION = [line.strip() for line in open("VERSION")][0]


setup(
    name='clinical-variant-ark',
    version=VERSION,
    description='A Python client for the Clinical Variant Ark',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/genomicsengland/pyark',
    download_url="https://github.com/genomicsengland/pyark/archive/v{}.tar.gz".format(VERSION),
    license='Apache',
    author=['Pablo Riesgo Ferreiro', 'Kevin Savage', 'William Bellamy'],
    author_email='pablo.riesgo-ferreiro@genomicsengland.co.uk',
    install_requires=[
        'requests==2.27.1; python_version<"3"',
        'requests>=2.27.1; python_version>="3.6"',
        'furl==2.1.3; python_version<"3"',
        'furl>=2.1.3; python_version>="3.6"',
        'gelreportmodels==7.8.1; python_version<"3"',
        'gelreportmodels>=8.0.0; python_version>="3.6"',
        'future>=0.18.3,<0.19'
    ],
    tests_require=test_deps,
    extras_require={'test': test_deps, 'pandas': ['pandas==0.24.2; python_version < \'3\'', 'pandas>=1.0.5; python_version >= \'3.6\'']},
    keywords=['CVA', 'pyark', 'clinical variant ark', 'Genomics England'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

      ]
)
