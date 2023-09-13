from setuptools import setup, find_packages
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name="mpu-servocontrol",
    version="0.1.2",
    description="beta version",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Radu Alexandru",
    author_email="radual3xandru6@gmail.com",
    license="MIT",
    packages=find_packages(include=["mpu_servocontrol"]),
    install_requires=["smbus"]
)
