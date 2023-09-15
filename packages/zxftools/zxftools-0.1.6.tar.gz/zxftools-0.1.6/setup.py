from setuptools import setup, find_packages

setup(name='zxftools',  # 包名
      version="0.1.6",  # 版本号
      author='zhaoxuefeng',  # 作者
      packages=['zxftools'],  # 包列表
      py_modules=[],
      install_requires=['tritonclient[all]'],
      description='工具包',
      )


