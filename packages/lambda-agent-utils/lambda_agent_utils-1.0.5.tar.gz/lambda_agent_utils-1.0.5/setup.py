from setuptools import setup, find_packages

long_description = """
Lambda Utilities
================

Lambda Utilities is a Python package that provides utility functions for handling input and output in AWS Lambda functions triggered by various sources, including API Gateway, AWS Service Kafka, and CLI.

Features
--------

- Easily extract and format input parameters based on the trigger source.
- Send output data back to the appropriate source with proper formatting.
- Supports AWS Lambda functions for various use cases.

Usage
-----

To use Lambda Utilities in your AWS Lambda functions, follow these steps:

1. Import the `input_handler` and `output_handler` modules.
2. Use these modules to streamline input and output handling.

License
-------

This project is licensed under the MIT License.
"""

setup(
    name='lambda_agent_utils',
    version='1.0.5',
    description='Lambda utils',
    author='Pradeep',
    author_email='pradeep@incaendo.com',
    packages=find_packages(),
    install_requires=[
        'kafka-python==2.0.2',
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)