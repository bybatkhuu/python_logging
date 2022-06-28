# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.util import convert_path


_package_name = 'beans_logging'

_namespace_dict = {}
_version_path = convert_path(f'{_package_name}/__version__.py')
with open(_version_path) as _version_file:
    exec(_version_file.read(), _namespace_dict)
_package_version = _namespace_dict['__version__']

setup(
    name = _package_name,
    packages = [_package_name],
    version = f"{_package_version}",
    license='MIT',
    description = 'Loguru based custom logging package (beans_logging) for python projects.',
    long_description = open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author = 'Batkhuu Byambajav',
    author_email = 'batkhuu10@gmail.com',
    url = 'https://github.com/bybatkhuu/python_logging',
    download_url = f'https://github.com/bybatkhuu/python_logging/archive/v{_package_version}.tar.gz',
    keywords = [_package_name, 'loguru', 'logging', 'logger', 'logs', 'log', 'print', 'custom logging'],
    install_requires = [
        'python-dotenv>=0.20.0',
        'PyYAML>=6.0',
        'loguru>=0.6.0'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
