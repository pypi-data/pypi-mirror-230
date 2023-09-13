# sourcery skip: path-read
from setuptools import find_packages, setup

with open('./README.md') as fp:
    long_description = fp.read()
    
setup(
    name="simpleGpyT",
    version="0.1.3",
    description="A simplified object-oriented interface for OpenAI's chat completion API.",
    packages=find_packages(where="SimpleGPyT"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AJWestley/SimpleChat",
    author="AJ Westley",
    author_email="alexanderjwestley@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    install_requires=["openai >= 0.28.0"],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
    python_requires=">=3.10",
)