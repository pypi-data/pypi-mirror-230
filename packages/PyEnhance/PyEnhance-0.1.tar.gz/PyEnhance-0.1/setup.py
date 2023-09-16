from setuptools import setup, find_packages

setup(
    name='PyEnhance',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'colorama'
    ],
    author='Not A Bird',
    description='A collection of essential scripts for any python project.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BirdsAreFlyingCameras/PyEnhance',
)
