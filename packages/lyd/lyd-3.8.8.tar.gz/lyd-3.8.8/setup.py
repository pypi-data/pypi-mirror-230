import os
import distro
import shutil
from setuptools import setup, find_packages
from setuptools.command.install import install

setup(
    name="lyd",
    version="3.8.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
                "lyg","tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows"
    ],
    author="LYG.AI",
    author_email="team@lyg.ai",
    url="https://lyg.ai",
)

