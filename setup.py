'''Setup file for adh-mng Azure Dedicated Hosts management library'''
from setuptools import setup

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    LONG_DESCRIPTION = open('README.md').read()


setup(name='adh-mng',
      version='0.10.0',
      description='Azure Dedicated Hosts management library',
      long_description=LONG_DESCRIPTION,
      url='http://github.com/zivraf',
      author='zivraf',
      author_email='zivraf',
      license='MIT',
      packages=['azuadh_mng'],
      install_requires=[
          'adal',
          'requests',
      ],
      zip_safe=False)
