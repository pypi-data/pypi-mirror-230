from setuptools import setup, find_packages

setup(
    name='ble_scanner',
    version='3.0',
    packages=find_packages(),
    install_requires=[
        'bleak',
        # other dependencies
    ],
)
