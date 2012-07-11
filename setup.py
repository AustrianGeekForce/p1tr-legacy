#!/bin/python3

try:
    from setuptools import setup, find_packages
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='P1tr',
        version='0.1alpha',
        description='A modular irc bot.',
        author='Christian Ortner',
        author_email='chris.ortner@gmail.com',
        license='MIT',
        url='https://github.com/howard/p1tr',
        install_requires=['oyoyo'],
        include_package_data=True,
        entry_points="""
        [console_scripts]
        p1tr = p1tr.p1tr:main
        """
)

