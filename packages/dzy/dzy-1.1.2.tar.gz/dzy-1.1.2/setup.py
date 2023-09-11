"""
Setup dzy package
"""
from setuptools import find_packages, setup

setup(
    name="dzy",
    version="1.1.2",
    description="dzy Python package",
    author="dzy",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "gcsfs>=2021.8.1,<2023.7",
        "google-cloud-bigquery>=2.23.2,<4",
        "google-cloud-secret-manager>=2.7.2,<3",
        "google-cloud-storage>=1.41.1,<3",
        "pandas>=1.3.2,<3",
        "pyarrow>=5.0.0,<14",
        "pytz>=2021.1,<2023.4",
        "pyyaml>=6.0,<7"
    ]
)
