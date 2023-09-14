from setuptools import setup, find_packages

setup(
    author="Raúl Guerrero",
    description ="package for siesta utilities",
    name="siesta_tools",
    version='0.1.0',
    packages=find_packages(include=["utilities","utilities.*","electronic_utils","electronic_utils*"]),
    install_requires=[
        "pandas>=1.5.3",
        "numpy>=1.23.5",
        "ase>=3.22.1",
        "sisl>=0.13"
    ],
    python_requires='>=3.8',
)