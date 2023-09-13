import setuptools
from venezuela_dollar_price import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding="utf-8") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="venezuela-dollar-price",
    version=__version__,
    author="Carlos Osuna",
    description="A package to get the dollar price in Venezuela",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Carlososuna11/Venezuela-dollar-price",
    project_urls={
        "Bug Tracker": "https://github.com/Carlososuna11/Venezuela-dollar-price/issues",
        "repository": "https://github.com/Carlososuna11/Venezuela-dollar-price"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)
