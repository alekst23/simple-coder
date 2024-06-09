from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='simple-coder',
    version='1.5',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
)
