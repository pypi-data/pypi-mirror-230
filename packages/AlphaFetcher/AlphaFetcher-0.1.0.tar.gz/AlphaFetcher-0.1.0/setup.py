from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="AlphaFetcher",
    version="0.1.0",
    author="Jose Gavalda-Garcia",
    author_email="jose.gavalda.garcia@vub.be",
    description="This package allows interface with the AlphaFold Protein Structure Database. "
                "This package allows the download of entries' metadata an AlphaFold files (e.g. mmCIF, PAE, PDB...)",
    license="OSI Approved :: GNU General Public License v3 (GPLv3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Jose Gavalda-Garcia",
    maintainer_email="jose.gavalda.garcia@vub.be",
    url="https://bitbucket.org/bio2byte/alphafetcher/",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Development Status :: 4 - Beta"
    ],
    python_requires=">=3.6, <3.12",
    install_requires=[
        "requests",
        "tqdm",
    ],
)
