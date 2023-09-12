from setuptools import *
import setuptools

setup(
    name='cmi_extract_tool',# 需要打包的名字,即本模块要发布的名字
    version='v1.0',#版本
    description='cmi_extract_tool for oval tech', # 简要描述
    py_modules=['classify','cmi_email', 'extract', 'helper', 'main', 'setup'],   #  需要打包的模块
    author='Yuheng Wu', # 作者名
    author_email='wuyuheng@oval-tech.com',   # 作者邮件
    url='https://git.pharm-hub.com.cn:8443/web-crawling/python', # 项目地址,一般是代码托管的网站
    requires=['imaplib', 'imap_tools', 'pandas'], # 依赖包,如果没有,可以不要
    packages=setuptools.find_namespace_packages(include=["config", "config.*", "src.*", "src"], ),
    include_package_data=True,
    license='OVAL TECH'
)