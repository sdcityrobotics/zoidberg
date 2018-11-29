from setuptools import setup

setup(name='fish_hawk',
      version='0.1',
      description='Pixhawk interface for zoidberg submarine',
      url='http://github.com/nedlrichards/fish_hawk',
      author='Edward Richards',
      author_email='edwardlrichards@gmail.com',
      license='MIT',
      packages=['fish_hawk'],
      install_requires=[
          'pymavlink',
          'pyserial',
          'setuptools',
          'hidapi'
      ],
      zip_safe=False)
