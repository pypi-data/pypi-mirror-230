from setuptools import setup ,find_packages

setup(
     name='logatta-countries',
    version='0.2',
    author='ashrf Obiedat',
    packages=find_packages(),
    install_requires=[
        'Django',
        'djangorestframework',
        # Add other dependencies here
    ],
)