from setuptools import setup

setup(
    name="pesapal_py",
    version="0.0.1",
    description="A minimalist python library that integrates with PesaPal's API 3.0 - JSON APIs (https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)",
    author="Brian Owino Otieno",
    author_email="brian@sabce.co.ke",
    packages=["pesapal_py"],
    install_requires=["requests"],
)
