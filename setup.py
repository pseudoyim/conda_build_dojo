#!/usr/bin/env python

'''
Assume this repo will be installed in dev mode. Not quite ready yet for packaging.
Use:
  pip instll -e .
'''
import setuptools

setuptools.setup(
    name='conda_build_dojo',
    version='0.1.0',
    description="Conda-Build Dojo guides you through debugging scenarios encountered during package building.",
    url='https://github.com/pseudoyim/conda_build_dojo',
    author="Paul Yim",
    author_email='paul.j.yim@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD-3-clause License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=setuptools.find_packages(),
    install_requires=[
		'conda',
		'conda-build',
		'gitpython',
		'pandas',
		'pyyaml',
		'tabulate',
        ],
    entry_points={
        'console_scripts': [
            'dojo = dojo.__main__:main',
        ]
    },
    license="BSD 3-clause",
)
