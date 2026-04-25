from setuptools import setup, find_packages

setup(
    name="numerical_workbench",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.26",
        "matplotlib>=3.8",
        "pyfiglet>=1.0"
    ],
)
