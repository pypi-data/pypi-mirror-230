import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gedi_tools",
    version="0.0.1",
    author="Joseph Emile Honour Percival",
    author_email="ipercival@gmail.com",
    description="A python package to assist working with GEDI data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iosefa/gediTools",
    project_urls={
        "Bug Tracker": "https://github.com/iosefa/gediTools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pandas~=1.5.3',
        'geopandas~=0.12.2',
        'requests~=2.28.2',
        'tqdm~=4.64.1',
        'h5py~=3.8.0',
        'numpy~=1.24.2'
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.10"
)
