from setuptools import find_packages, setup

setup(
    name='alpcom_api',
    packages=find_packages(include=['alpcom_api']),
    install_requires=[
        'requests==2.31.0',
        'pydantic==2.1.1',
        'pyjwt==2.8.0',
        'websockets==11.0.3'
    ],
    version='1.0.2',
    description='ALP.com API Python',
    author='ALP.com',
    license='MIT',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
