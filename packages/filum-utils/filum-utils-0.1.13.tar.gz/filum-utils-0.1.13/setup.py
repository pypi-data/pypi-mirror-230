import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'filum_analytics'))

VERSION = "0.1.13"
DESCRIPTION = "Filum Utils"
LONG_DESCRIPTION = "Filum Utils"

install_requires = [
    "requests==2.25.1",
    "filum-analytics-python==1.1.1",
    "glom==20.11.0",
]

setup(
    name="filum-utils",
    version=VERSION,
    author="Hiep Nguyen",
    author_email="<hnguyen@filum.ai>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
