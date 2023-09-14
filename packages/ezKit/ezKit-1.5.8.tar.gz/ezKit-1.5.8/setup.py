from setuptools import find_packages, setup

setup(
    name='ezKit',
    version='1.5.8',
    author='septvean',
    author_email='septvean@gmail.com',
    description='Easy Kit',
    packages=find_packages(exclude=['deprecated', 'documents', 'examples', 'tests']),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'loguru>=0.7.0',
        'tomlkit>=0.12.0'
    ]
)
