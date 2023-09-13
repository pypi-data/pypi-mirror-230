from setuptools import setup, find_packages

setup(name='kdb-testing',
      version='0.0.1',
      url='https://github.com/Trucnt/kdb-core',
      Metadata_Version='2.3',
      license='MIT',
      author='Truc Nguyen',
      author_email='trucnt88@gmail.com',
      description='The automation testing framework using Selenium, Python and Pytest. '
                  'This developed base on POM pattern',
      packages=find_packages(exclude=['data', 'docs', 'examples']),
      # long_description=open('README.md').read(),
      zip_safe=False)
