# coding: utf-8

from setuptools import setup

REQUIRES = ["numpy","pandas"]

setup(
    name='dcovlib',
    version='1.2.0',
    python_requires='>=3.6',
    description='convert numpy to ird file, or convert ird to numpy\
    V1.1.0 add Excel',
    platforms='Independant',
    author='Sun ling', # 作者
    author_email="ling.sun-01@qq.com",
    url="https://github.com/SheepBreedingLab-HZAU/dcovlib",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIRES,
    packages=['dcovlib']
)

