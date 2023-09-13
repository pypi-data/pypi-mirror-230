# -*- coding: utf-8 -*-
"""
@Time ： 2023/9/12 21:46
@Auth ： Alan Gong
@File ：setup.py.py
@IDE ：PyCharm
"""
from time import time
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ZYYA_Codes",
    version="2023.0.0.0",
    author="Yitong Gong",
    author_email="yitong.gong@qq.com",
    description="Python codes for ZYYA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"}
)
