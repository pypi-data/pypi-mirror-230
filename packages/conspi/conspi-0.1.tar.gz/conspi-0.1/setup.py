from setuptools import setup, find_packages

setup(
    name='conspi',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'jieba',
        'scikit-learn',
    ],
)