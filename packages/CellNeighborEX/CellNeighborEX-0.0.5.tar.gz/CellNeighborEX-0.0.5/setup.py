import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CellNeighborEX", 
    version="0.0.5", 
    author="Hyobin Kim", 
    author_email="hbkim20005@gmail.com", 
    description="library for neighbor-dependent gene expression analysis", 
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hkim240/CellNeighborEX", 
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8,<3.11',
)