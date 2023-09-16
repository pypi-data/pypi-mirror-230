#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='macroplot-python',
    version='1.1',
    description='Macroplot Python Client',
    long_description='Access Macroplot APIs from Python.',
    url='https://macroplot.com',
    license='MIT',
    author='Sebastian Nogara',
    author_email='snogara@macroplot.com',
    packages=find_packages(),
    install_requires=[
        'six>=1.0.0',
        'requests>=2.0.0',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
)
