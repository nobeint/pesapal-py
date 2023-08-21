from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pesapal-py",
    version="0.1.1",
    description="A minimalist python library that integrates with PesaPal's API 3.0 - JSON APIs (https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Brian Owino Otieno",
    author_email="brian.otieno709@gmail.com",
    packages=["pesapal_py"],
    url="https://github.com/twais/pesapal-py",
    download_url="https://github.com/twais/pesapal-py/archive/refs/tags/v0.0.1.tar.gz",
    install_requires=["requests"],
)
