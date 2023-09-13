from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Operating System :: Unix',
  'Operating System :: MacOS :: MacOS X',
  'Operating System :: Microsoft :: Windows :: Windows 10'
]
 
setup(
  name='iotellme',
  version='1.7.0',
  description='Helping developers easily build, test, manage, and scale applications internet of things faster than ever before.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://iotellme.io/',  
  author='iotellme LLC',
  author_email='abdulmalektaleb2022@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['iotellme','Token','Send','Read','Write1'],
  packages=find_packages(),
  install_requires=["requests","jsons"] 
  )

