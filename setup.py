from setuptools import setup

setup(name='zoidberg',
      version='0.1',
      description='Pixhawk interface for zoidberg submarine',
      url='http://github.com/nedlrichards/fish_hawk',
      author='San Diego city robotics club',
      author_email='sdcrobotics@gmail.com',
      license='MIT',
      packages=['zoidberg'],
      install_requires=[
          'pymavlink>=2.3.4',
          'pyserial'
      ],
      zip_safe=False)
