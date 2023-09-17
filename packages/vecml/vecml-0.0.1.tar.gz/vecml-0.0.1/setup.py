from setuptools import setup

setup(name='vecml',
      version='0.0.1',
      description='The VecML client',
      url='http://github.com/vecml/vecml',
      author='VecML Authors',
      author_email='support@vecml.com',
      license='Apache-2.0',
      packages=['vecml'],
      install_requires=[
        'grpcio',
        'numpy',
        'scipy',
        'tqdm',
        'protobuf'
      ],
      zip_safe=False)
