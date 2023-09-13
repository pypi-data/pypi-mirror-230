# coding: utf-8
from setuptools import setup, find_packages
 
setup(
    name="HDLpy",
    author="ChenHaha",
    version="1.0.0",
    author_email="596838981@qq.com",
    packages=find_packages(),
    description="HDLpy",
    long_description="HDLpy",
    license='Apache2.0',
    install_requires=[
        'requests',
        'tqdm',
        'pyvcd',
    ],
)
