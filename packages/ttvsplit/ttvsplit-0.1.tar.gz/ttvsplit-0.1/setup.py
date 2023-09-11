from setuptools import setup, find_packages

setup(
    name="ttvsplit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    author="Aryan Sakhala",
    author_email="ryansakhala@gmail.com",
    description="A simple library to split data into train, test, and validation sets.",
    keywords="train test validation split data machine learning",
    url="https://github.com/ryansakhala/ttvsplit",   # if you have a GitHub repo for this
)
