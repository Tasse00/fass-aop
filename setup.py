from setuptools import setup

from fass_aop import VERSION

setup(
    name='FAss-AOP',
    version=VERSION,
    description=('面向切面编程, FAss项目的运行时补充'),
    packages=["fass_aop"],
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    author='Aengine',
    author_email='zhangzheng@aengine.com.cn',
    maintainer='Carl.Zhang',
    maintainer_email='zhangzheng@aengine.com.cn',
    platforms=["all"],
    url='http://gitlab.aengine.com.cn/aengine/fass-aop',
)
