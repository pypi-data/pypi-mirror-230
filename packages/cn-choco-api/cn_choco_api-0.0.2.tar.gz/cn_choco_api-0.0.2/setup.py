import os
import sys

from setuptools import find_packages, setup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

setup(
    name='cn_choco_api',
    version='0.0.2',
    packages=find_packages(),
)
