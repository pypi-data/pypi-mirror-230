import os
from setuptools import setup, find_packages

setup(
    name='shengtengconverter',
    version='1.0.3',
    description='A simple converter for Shengteng',
    author='zhangzhiyang',
    author_email='1963306815@qq.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['onnx>=1.13.1','torch>=1.11.0'],
    url='https://github.com/1963306815/shengtengconverter'
)