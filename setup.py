from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='moleculai',
    version='1.1.0',
    packages=find_packages('moleculai'),
    package_dir={'': 'moleculai'},
    install_requires=requirements,
)
