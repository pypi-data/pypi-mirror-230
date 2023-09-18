from setuptools import setup

setup(name='kristpy',
      version='0.0.1',
      description='A simple krist websocket api wrapper for python',
      url='http://github.com/scmcgowen/kristpy',
      author='Herr Katze',
      author_email='scmcgowen@gmail.com',
      license='MIT',
      packages=['src/kristpy'],
      install_requires=[
            'aiohttp',
            'certifi',
      ],
      zip_safe=False)