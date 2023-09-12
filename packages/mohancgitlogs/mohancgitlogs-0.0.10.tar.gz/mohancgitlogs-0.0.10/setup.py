from setuptools import setup, find_packages

setup(
    name="mohancgitlogs",
    author="Mohan Chinnappan",
    summary="Gets the git logs", 
    version="0.0.10",
    packages=find_packages(),
    install_requires=[ 'pyperclip==1.8.2' ],
)

