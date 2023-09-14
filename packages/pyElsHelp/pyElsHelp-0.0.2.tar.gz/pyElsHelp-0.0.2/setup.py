from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='pyElsHelp',
  version='0.0.2',
  author='the_sloth_bear',
  author_email='molnychess@yandex.ru',
  description='This is the module for ELSCHOOL diary',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/theslothbear/Elschool-Help-Bot',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='pyElsHelp',
  project_urls={
    'GitHub': 'https://github.com/theslothbear'
  },
  python_requires='>=3.6'
)