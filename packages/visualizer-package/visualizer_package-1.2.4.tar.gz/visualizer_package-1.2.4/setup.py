from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = "visualizer_package",
    version='1.2.4',
    description='Python Distribution Utilities',
    author='Satyam@UCSD',
    author_email='sas043@ucsd.edu',
    long_description=long_description,
    long_description_content_type="text",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    install_requires=[],
    extras_requires={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.0",
)