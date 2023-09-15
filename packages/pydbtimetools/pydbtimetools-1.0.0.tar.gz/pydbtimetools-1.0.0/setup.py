from setuptools import setup,find_packages

setup(
    name='pydbtimetools',
    version='1.0.0',
    description='A package for MySQL and MongoDB and Redis and Date utilities',
    author='zxw',
    author_email='your@email.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'DBUtils>=3.0.3',
        'PyMySQL>=1.0.2',
        'PyYAML>=6.0',
        'loguru>=0.7.0',
        'pandas>=1.1.5',
        'redis>=4.3.6',
        'pymongo>=4.1.1',
    ],
)
