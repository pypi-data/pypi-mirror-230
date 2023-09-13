from setuptools import setup, find_packages

setup(
    name='cloudprovider',
    version='1.0.0',
    packages= find_packages(),
    author="Maha Arunachalam",
    description="Multi cloud provider",
    long_description="Multi Cloud provider",
    install_requires=[
        'boto3',  # Add any other required dependencies here
    ],
    py_modules=["aws"],
    package_dir = {"": "cloudprovider/src"}
)
