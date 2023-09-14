from setuptools import setup, find_packages

setup(
    name='cloudprovider',
    packages= find_packages(),
    version='1.0.1',
    author="Maha Arunachalam",
    description="Multi cloud provider",
    long_description="Multi Cloud provider",
    install_requires=[
        'boto3',  # Add any other required dependencies here
        'azure-identity',
        'azure-mgmt-compute',
    ],
    license='MIT',
)
