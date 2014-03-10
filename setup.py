from setuptools import setup

required_modules = ['mongoengine']

setup(name='acts_as_state_machine',
      version='0.1',
      description='Python State Machines for Humans',
      url='http://github.com/jtushman/acts_as_state_machine',
      author='Jonathan Tushman',
      author_email='jonathan@zefr.com',
      install_requires=required_modules,
      license='MIT',
      packages=['acts_as_state_machine'],
      zip_safe=False)