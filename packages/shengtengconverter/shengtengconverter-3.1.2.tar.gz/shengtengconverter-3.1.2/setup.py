import os
from setuptools import setup, find_packages

setup(
    name='shengtengconverter',
    version='3.1.2',
    description='A simple converter for Shengteng',
    author='zhangzhiyang',
    author_email='1963306815@qq.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['numpy>=1.24.2', 'onnx>=1.13.1', 'onnx_tf>=1.10.0', 'onnxruntime-gpu', 'setuptools>=56.0.0', 'tensorflow>=2.11.0', 'tf2onnx>=1.13.0', 'torch>=1.11.0', 'torchvision>=0.15.2', 'tensorflow_probability'],
    url='https://github.com/1963306815/shengtengconverter'
)
