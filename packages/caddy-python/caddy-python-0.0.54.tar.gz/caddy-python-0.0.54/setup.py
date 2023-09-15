from setuptools import setup, find_packages

setup(
    name='caddy-python',
    version='0.0.54',
    description='Python SDK for Caddy',
    author='Caddy',
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    python_requires='>=3.6',
)