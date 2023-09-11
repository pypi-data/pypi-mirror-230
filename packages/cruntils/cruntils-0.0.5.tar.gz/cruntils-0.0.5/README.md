# Introduction

A collection of utilities.

# Updating package

py -m build
py -m twine upload dist/*

# Package Creation

Okay, this guide was also really useful:
https://packaging.python.org/en/latest/tutorials/packaging-projects/

Used the following guide to create the package:
https://python-packaging.readthedocs.io/en/latest/minimal.html

Had some trouble registering, apparently you don't need to pre-register anymore.

Created a .pypirc file in my user base directory and added the follow:

[pypi]
username:Nambarc
password:********

The used the following command to upload to PyPi:
py setup.py register sdist upload -r https://www.python.org/pypi

Had a little trouble uploading it, I think the name "crutils" is taken...
    Will try "cruntils" instead.

py -m pip install --upgrade build
py -m build
py -m pip install --upgrade twine
py -m twine upload dist/*

Yay, this worked!
