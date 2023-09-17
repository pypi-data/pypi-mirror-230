from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name="maullick_basic_calculator",
  version='0.0.1',
  description = 'This is a Calculator Program that can easily calculate any expression with one function.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://upload.pypi.org/legacy/',  
  author='Maullick Kathuria',
  author_email='maullickkathuria23@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='calculate', 
  packages=find_packages(),
  install_requires=[''] 
)
