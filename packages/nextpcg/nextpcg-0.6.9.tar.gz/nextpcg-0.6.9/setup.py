#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='nextpcg',
    author='GenesisGroup',
    version='0.6.9',
    license='MIT',

    description='pypapi module in NextPCG',
    long_description='''
    What is NextPCG?
    Fast Track to Game Content Generation
    
    To meet the growing demand for immersive games with vast amounts of content, game developers can use a procedural 
    approach with NextPCG to create high-quality games efficiently, while meeting deadlines and containing costs.
    
    NextPCG is a cloud-based solution that enhances game engines' AIGC and procedural content generation capabilities. 
    It provides comprehensive toolsets for creating game content out-of-the-box, along with an efficient pipeline 
    and the ability to generate Vastworlds.
    
    The NextPCG Features
    - Provide rich out-of-the-box toolsets for game content generation.
    - Provide a product standard efficient pipeline for open-world game levels generation.
    - Support one-click Vastworlds generation through a cloud-based platform.
    ''',
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