from setuptools import find_packages, setup
setup(
    name='mypythonlibdelta4',
    packages=find_packages(include=['mypythonlib']), 
    version='0.1.0',
    description='My first Python library',
    author='Ashish',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner']
)