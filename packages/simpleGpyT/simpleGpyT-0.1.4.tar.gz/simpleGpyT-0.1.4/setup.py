# sourcery skip: path-read
from setuptools import find_packages, setup

VERSION = "0.1.4"

with open('./README.md') as fp:
    long_description = fp.read()

setup(
    name="simpleGpyT",
    version=VERSION,
    author="AJ Westley",
    author_email="<alexanderjwestley@gmail.com>",
    description="A simplified object-oriented interface for OpenAI's chat completion API.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/AJWestley/SimpleChat",
    packages=find_packages(),
    install_requires=["openai >= 0.28.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ]
)