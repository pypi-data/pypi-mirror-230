#############################################
# File Name: setup.py
# Author: LiangjunFeng
# Mail: zhumavip@163.com
# Created Time:  2018-4-16 19:17:34
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "wydtools",      #这里是pip项目发布的名称
    version = "0.8.7",  #版本号，数值大的会优先被pip
    keywords = ("pip", "wydtools"),
    description = "Discharge voltage curves",
    long_description = "Discharge voltage curves",
    license = "MIT Licence",

    author = "WYD",
    author_email = "wangyudong2018@ia.ac.cn",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []          #这个项目需要的第三方库
)