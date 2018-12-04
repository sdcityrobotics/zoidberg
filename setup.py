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
          'numpy',
          'pymavlink',
          'pyserial',
          'setuptools',
          'hidapi'
      ],
      extras_require={
          'controller': ["hidapi"],
          'zed': ["pyzed", "cv2"],
          },
      zip_safe=False)
