from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='column_cleaner',
    version='0.0.2',
    description='A column cleaner, which will clean the numerical values and spaces',
    author= 'KIE Square Analytics',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['column cleaner', 'number cleaner', 'space cleaner'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['column_cleaner'],
    package_dir={'':'src'},
    install_requires = [
        'pandas',
    ]
)