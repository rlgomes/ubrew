"""
setup.py
"""
from setuptools import setup, find_packages 

from ubrew.cli import __VERSION_STRING

setup (
    name='ubrew',
    version=__VERSION_STRING,
    author='Rodney Gomes',
    author_email='rodneygomes@gmail.com',
    url='',
    install_requires = [
                        'beautifulsoup4',
                        'colorama',
                       ],
    tests_require = [
                     'parameterizedtestcase'
                    ],
    test_suite="tests",
    keywords = [''],
    py_modules = ['ubrew'],

    packages = find_packages(exclude=['test']),
    license='Apache 2.0 License',
    description='',
    long_description='',

    scripts = [
        'scripts/ubrew.sh'
    ],
)
