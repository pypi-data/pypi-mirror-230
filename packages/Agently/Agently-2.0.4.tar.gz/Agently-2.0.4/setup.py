import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "Agently",
    version = "2.0.4",
    author = "Maplemx",
    author_email = "maplemx@gmail.com",
    description = "Agently, a framework to build applications based on language model powered intelligent agents.",
    long_description = "https://github.com/Maplemx/Agently",
    url = "https://github.com/Maplemx/Agently",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)