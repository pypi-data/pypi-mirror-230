import setuptools
from pathlib import Path

setuptools.setup(
    name="rafpdf2text",
    version=0.1,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["test", "data"])
)
