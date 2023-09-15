#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='nextpcg',
    author='GenesisGroup',
    version='0.6.8',
    license='MIT',

    description='pypapi module in NextPCG',
    long_description='''Create by AI: 
    The pypapi module in NextPCG is a powerful tool that allows users to create sophisticated programs and applications 
    with ease. It provides a comprehensive suite of features and commands that makes coding much simpler and faster. 
    With the help of this module, users can quickly and easily develop programs and applications with advanced 
    capabilities, such as natural language processing, artificial intelligence, and other complex tasks. 
    In addition, the pypapi module makes it easy to create programs and applications that are compatible with 
    different platforms and operating systems, ensuring that users can deploy their creations on a variety of platforms. 
    All in all, the pypapi module in NextPCG is a great tool for developers who want to quickly and easily create 
    complex applications.''',
    author_email='cheneyshen@tencent.com',
    url='https://nextpcg.notion.site/Wiki-384dc1d9d9f64306bd8774ff1138f618?pvs=4',

    include_package_data=True,

    # packages=setuptools.find_packages(exclude=["dson_test", "dson_generator", "dispatch"]),
    # packages=setuptools.find_packages(where=['pypapi']),
    packages=['pypapi', 'common'],
    # package_dir={'pypapi':'pypapi'},
    # package_data={'pypapi.pantry':['*']},

    entry_points={
        'console_scripts':[
            'nextpcg = pypapi.__main__:entry'
        ]
    },
    install_requires=[
        "numpy",
        "pillow",
        "requests",
        "pyyaml",
        "importlib_resources"
    ],

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        # 'License :: OSI Approved :: MIT License',
        # 'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        # 'Programming Language :: Python :: 3.9',
        # 'Programming Language :: Python :: 3.10',

        'Topic :: Software Development :: Libraries'
    ],

    python_requires=">=3.6",
    zip_safe=True,
)