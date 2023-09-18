#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'tensorflow-datasets>=4.1.0']

test_requirements = [ ]

setup(
    author="yunotao",
    author_email='yunotao@163.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A python lib to implement sesr",
    entry_points={
        'console_scripts': [
            'sesr_tool=sesr_tool.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sesr_tool',
    name='sesr_tool',
    packages=find_packages(include=['sesr_tool', 'sesr_tool.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/yunot/sesr_tool',
    version='0.1.0',
    zip_safe=False,
)
