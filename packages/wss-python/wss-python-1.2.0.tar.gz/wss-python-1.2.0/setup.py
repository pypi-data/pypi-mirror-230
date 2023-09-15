from setuptools import setup

setup(name='wss-python',
      version="1.2.0",
      description="文叔叔",
      author='sanfeng',
      author_email='2669291603@qq.com',
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
