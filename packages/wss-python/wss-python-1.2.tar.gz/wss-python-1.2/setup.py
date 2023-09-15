from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setup(name='wss-python',
      version="1.2",
      description="一个好用的命令行版文叔叔上传下载工具",
      keywords='python、PyPi source、terminal',
      url="https://gitee.com/i-tok/wss-python",
      author='sanfeng',
      author_email='2669291603@qq.com',
      license='MIT',
      long_description=long_description,
      long_description_content_type="text/markdown",
      include_package_data=True,
      zip_safe=True,
      classifiers=[],
      packages=["wss"],
      install_requires=[
          'requests', 'base58', 'pycryptodomex', 'docopt'
      ],
      entry_points={
          'console_scripts': [
              'wss = wss.wss:main'
          ]
      },
      )
