from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='knot_xyz',
    version='0.0.1',
    packages=setuptools.find_packages(),
    license='MIT',
    author='YANG Jiansong',
    author_email='jsyang-c@my.cityu.edu.hk',
    description='A small example package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)