import os
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('state_machine'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

required_modules = []

setup(name='state_machine',
      version='0.2.4',
      description='Python State Machines for Humans',
      url='http://github.com/jtushman/state_machine',
      author='Jonathan Tushman',
      author_email='jonathan@zefr.com',
      install_requires=required_modules,
      license='MIT',
      packages=['state_machine'],
      zip_safe=False)