import os
from setuptools import setup

setup(
    name="JokerSDK",
    version="0.0.38",
    author="0x96e63",
    description="A Simple SDK for Joker's Voice API.",
    long_description=open("README.md", "r", encoding="UTF-8").read(),
    long_description_content_type='text/markdown',
    url="https://github.com/0x96e63/JokerAPI-SDK",
    packages=[
        os.path.join(root).replace("\\", ".") for root, _, files in os.walk("JokerAPI") if "__init__.py" in files
    ]
)