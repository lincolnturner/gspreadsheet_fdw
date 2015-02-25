import subprocess
from setuptools import setup, find_packages, Extension

setup(
  name='gspreadsheet_fdw',
  version='0.0.1',
  author='Lincoln Turner',
  author_email='lincoln.turner@monash.edu',
  url='https://github.com/lincolnturner/gspreadsheet_fdw/',
  license='MIT',
  packages=['gspreadsheet_fdw']
)

