from setuptools import setup, find_packages

setup(
    name='aop',
    version="2.2.5",
    description='依靠meta_path实现的无倾入的AOP工具包',
    packages=find_packages(
        include=("aop*", )
    ),
    include_package_data=True,
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    author='Aengine',
    author_email='zhangzheng@aengine.com.cn',
    maintainer='Carl.Zhang',
    maintainer_email='zhangzheng@aengine.com.cn',
    platforms=["all"],
    url='http://gitlab.aengine.com.cn/aengine/fass-aop',
)
