import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tms-pypi",
    version="0.0.1",
    author="tms",
    author_email="tms@gmail.com",
    description="Tms pypi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IAnanevich/tms-python-py43",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)