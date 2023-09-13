from setuptools import setup, find_packages


with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="hdg_bavaria_boiler",
    version="0.1.0",
    author="Florian A. von Garrel",
    author_email="mail@florianvongarrel.de",
    url="https://github.com/fvgarrel/hdg-bavaria-boiler",
    description="Python client for the HDG Bavaria Boiler API",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
)