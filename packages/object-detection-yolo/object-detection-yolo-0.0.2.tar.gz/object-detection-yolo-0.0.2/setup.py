from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.2'

setup(
    name='object-detection-yolo', 
    version=VERSION,
    packages=find_packages(),
    install_requires = ['ultralytics==8.0.54'],

)