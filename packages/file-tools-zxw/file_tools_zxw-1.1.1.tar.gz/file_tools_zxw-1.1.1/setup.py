"""
# File       : setup.py
# Time       ：2023/9/14 15:29
# Author     ：xuewei zhang
# Email      ：jingmu_predict@qq.com
# version    ：python 3.8
# Description：
"""
from setuptools import setup, find_packages

setup(
    name="file_tools_zxw",
    version="1.1.1",
    packages=find_packages(),
    install_requires=[
        'xlwt',
        'fastapi',
        'psutil'
        # 依赖的其他包，例如：'requests>=2.0.0'
    ],
    author="XueWei Zhang",
    author_email="tonson_predict@qq.com",
    description="常用的文件操作的中文工具包,如文件查找,创建文件夹, 文件夹查找等.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypackage",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
