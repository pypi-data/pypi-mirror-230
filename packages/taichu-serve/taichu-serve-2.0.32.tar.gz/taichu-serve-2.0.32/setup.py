from datetime import date
import sys
from setuptools import setup, find_packages
# pylint: disable = relative-import
import taichu_serve

pkgs = find_packages()

if __name__ == '__main__':
    name = 'taichu-serve'

    requirements = ['grpcio', 'grpcio-tools', 'protobuf', 'Flask', 'gunicorn', 'requests',
                    'opentelemetry-api', 'opentelemetry-sdk', 'opentelemetry-exporter-otlp',
                    'opentelemetry-instrumentation-flask', 'opentelemetry-instrumentation-grpc']

    long_description = ''
    # with open('README.md', 'r') as f:
    #     long_description = f.read()

    setup(
        name=name,
        version='2.0.32',
        description='taichu serve is a tool for serving deep learning inference',
        long_description=long_description,
        author='taichu platform team',
        # author_email='noreply@noreply.com',
        python_requires=">=3.6.0",
        url='',
        keywords='Serving Deep Learning Inference AI',
        packages=pkgs,
        install_requires=requirements,
        entry_points={
            'console_scripts': ['taichu_serve = taichu_serve.command:cli']
        },
        include_package_data=True,

        # license='Apache License Version 2.0'
    )
