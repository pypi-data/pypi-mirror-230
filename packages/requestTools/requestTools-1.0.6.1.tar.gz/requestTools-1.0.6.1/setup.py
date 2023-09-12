from distutils.core import setup
from setuptools import find_packages
from os import path as os_path

this_directory = os_path.abspath(os_path.dirname(__file__))

# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

setup(name='requestTools',  # 包名
      version='1.0.6.1',  # 版本号
      description='http request tools',
      long_description=read_file('README.md'),
      long_description_content_type="text/markdown",  # 指定包文档格式为markdown
      author='trimNiu',
      author_email='fahongsun168@sina.com',
      url='',
      install_requires=[
        'requests'
      ],

      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )