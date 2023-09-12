from setuptools import setup, find_packages

setup(
    name="sawsi",
    version="2.2",
    packages=find_packages(),
    install_requires=[
        'boto3==1.28.43',
        'PyJWT==2.8.0',
        'requests==2.31.0'
    ],
)
