from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='innovation_serviceauth',
    version='1.0.0',
    license="Apache License",
    description="This package is an Indico Innovation IAM gRPC client to be imported by Indico Innovation API clients.",
    packages=['innovation_serviceauth'],
    author="Indico Innovation",
    author_email="dev@indicoinnovation.pt",
    url="https://github.com/INDICO-INNOVATION/indico_service_auth_python",
    package_dir={'innovation_serviceauth': 'innovation_serviceauth'},
    install_requires=[
        'grpcio==1.54.2',
        'grpcio-tools==1.54.2',
        'jwcrypto==1.5.0'
    ],
    python_requires=">=3.10",
    zip_safe=False
)