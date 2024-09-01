from setuptools import find_packages,setup

setup(
name='Job Portal Scraper',
version='0.0.1',
author='Ryan',
author_email='ryananthonymatthew@gmail.com',
packages=find_packages(),
install_requires=['pandas','numpy','selenium','time','re','datetime','ast']
)