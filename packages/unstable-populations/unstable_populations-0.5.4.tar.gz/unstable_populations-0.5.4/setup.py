from setuptools import setup

setup(
    name="unstable_populations",
    version="0.5.4",
    author="Marcel Haas,  Lisette Sibbald",
    author_email="datascience@marcelhaas.com",
    packages=["unstable_populations"],  # "unstable_populations.test"],
    url="http://pypi.python.org/pypi/unstable_populations/",
    license=open("LICENSE").read(),
    description="Package to calculate Unstable Population Indicator and related population stability indices.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy >= 1.0.0",
        "pytest",
    ],
)
