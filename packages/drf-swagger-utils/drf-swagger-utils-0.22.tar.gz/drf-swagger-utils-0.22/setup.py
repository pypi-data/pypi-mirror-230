from setuptools import setup, find_packages

setup(
    name='drf-swagger-utils',
    version='0.22',
    author='Chinni Raja Ammela',
    author_email='mr.chinniraja53@gmail.com',
    description='Custom Django REST framework generators',
    packages=['api_generators', 'api_generators.templates', 'api_generators.management', 'api_generators.management.commands'],
    include_package_data=True,
    install_requires=['Django>=1.11','click'],
    entry_points={
        'console_scripts': [
            'build = drf_swagger_utils.cli:build',
        ]
    },
)
