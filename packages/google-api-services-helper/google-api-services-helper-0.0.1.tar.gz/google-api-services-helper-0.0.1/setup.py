from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 7 - Inactive',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows',
  'Operating System :: POSIX :: Linux',
  'Operating System :: MacOS',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='google-api-services-helper',
  version='0.0.1',
  description='Work In progress! A package with functionalities to help you develop faster code using google apis',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Dulea Mihai-Alexandru',
  author_email='duleasoft@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='api', 
  packages=find_packages(),
  install_requires=[
    'google-api-python-client',
    'google-auth-httplib2',
    'google-auth-oauthlib'
  ] 
)