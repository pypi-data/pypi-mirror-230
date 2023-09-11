from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()




setup(
    name='ttvsplit',
    version='0.3',
    author_email="ryansakhala@gmail.com",
    description='A Train Test Val Split library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Aryan Sakhala',
    packages=find_packages(),
    install_requires=[
        "numpy"
    ]
)


