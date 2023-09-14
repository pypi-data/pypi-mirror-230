from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='Transformer_0501',
  version='0.0.1',
  author='Alex_g',
  author_email='magomedaliewk05@gmail.com',
  description='This is the simplest module for quick work with model.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/jaymody/picoGPT',
  packages=find_packages(),
  install_requires=['requests>=2.30.0'],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  python_requires='>=3.10'
)