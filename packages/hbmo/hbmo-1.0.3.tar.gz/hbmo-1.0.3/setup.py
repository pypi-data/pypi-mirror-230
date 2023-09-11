from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
  name = 'hbmo',
  packages = ['hbmo'],
  version = '1.0.3',
  license='MIT',
  description = 'implementation of HBMO and MHBMO optimization algorithms',
  long_description = readme,
  long_description_content_type='text/markdown',
  author = 'Ali Mahmoodi',
  author_email = 'ali.mahmoodi7872@gmail.com',
  url = 'https://github.com/alimahmoodi78/hbmo',
  download_url = 'https://github.com/alimahmoodi78/hbmo/archive/refs/tags/v1.0.tar.gz',
  keywords = ['Swarm-Based Optimization', 'Honey-Bee Mating Optimization'],
  install_requires=['numpy', 'matplotlib']
)