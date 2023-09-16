from setuptools import setup, find_packages

setup(
    name='totemlib',
    version='0.1.0.15',
    packages=find_packages(),
    install_requires=[
        # lista de dependencias
        'jproperties==2.1.1',
    ],
    author='Totem Bear',
    author_email='info@totembear.com',
    description='Base library for general uses',
)
