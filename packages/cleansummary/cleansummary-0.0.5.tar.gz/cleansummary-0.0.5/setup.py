from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='cleansummary',
  version='0.0.5',
  description='A simple package to get statistical summary of a pandas dataframe',
  long_description=open('Guide.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    long_description_content_type='text/markdown',
    url='',  
  author='Francis W. Onyango',
  author_email='fonyango.w@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='cleansummary', 
  packages=find_packages(),
  install_requires=[''] 
)