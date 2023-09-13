from setuptools import setup, find_packages

setup(
    name='AhpAnpLib',
    version='2.3.11',
    description='Analytic Hierarchy Process and Analytic Network Process Library',
    author='Creative Decisions Foundation',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'graphviz<=0.20.1',
        'matplotlib>=3.7.2',
        'networkx>=3.1',
        'numpy>=1.25.2',
        'openpyxl>=3.1.2',
        'pandas>=2.0.3',
        'pydot>=1.4.2',
        'Shapely>=2.0.1',
        'tabulate>=0.9.0',
        'XlsxWriter>=3.1.2'
    ],
)
