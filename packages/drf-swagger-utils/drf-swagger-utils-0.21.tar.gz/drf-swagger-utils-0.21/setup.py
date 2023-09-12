from setuptools import setup, find_packages

setup(
    name='drf-swagger-utils',
    version='0.21',
    author='Chinni Raja Ammela',
    description='Custom Django REST framework generators',
    packages=find_packages(),
    install_requires=['Django>=1.11','click'],
    entry_points={
        'console_scripts': [
            'build = drf_swagger_utils.cli:build',
        ]
    },
)
