
from setuptools import setup, find_packages

long_description = """
Nightwatch Logger
=================

Nightwatch Logger is a Python package that offers a versatile logging utility for Python applications. It simplifies log management by providing features for both file and console output. You can use this package to improve your application's logging capabilities with ease.

Features
--------

- Log messages to files and optionally to the console.
- Supports various log levels: DEBUG, INFO, WARNING, ERROR, and CRITICAL.
- Customize log file names and log levels according to your application's needs.
- Properly formats log entries with timestamps and log levels for clarity.
- Handles structured logging with dynamic data, including dictionaries, lists, strings, integers, floats, booleans, and None.
- Exception handling to gracefully manage errors during logging and message formatting.

Usage
-----

1. Import the package `from nightwatch import Nightwatch` 
2. Create an instance of the Nightwatch class `nightwatch = Nightwatch(log_file_name='app.log', log_level=logging.INFO)`

License
-------

This project is licensed under the MIT License.

"""

setup(
    name='nightwatch',
    version='1.0.2',
    description='Logging',
    author='Pradeep',
    author_email='pradeep@incaendo.com',
    packages=find_packages(),
    install_requires=[
        # List any external dependencies here if needed
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)