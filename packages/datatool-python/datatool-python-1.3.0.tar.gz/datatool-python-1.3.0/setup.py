from setuptools import setup, find_packages

from datatool.version import __version__


setup(
    name='datatool-python',
    version=__version__,
    description='A datatool library.',
    author='Alexander Khlebushchev',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'matplotlib>=3.6.0',
        'numpy>=1.23.3',
        'pandas>=1.5.0',
        'pycuda>=2022.1',
        'requests>=2.28.1',
    ],
)
