import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_cmip",
    version="4.1.0",
    author="Biobb developers",
    author_email="pau.andrio@bsc.es",
    description="biobb_cmip is the Biobb module collection to compute classical molecular interaction potentials.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_cmip",
    project_urls={
        "Documentation": "http://biobb_cmip.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/"
    },
    packages=setuptools.find_packages(exclude=['docs', 'test']),
    include_package_data=True,
    install_requires=[
        'biobb_common==4.1.0',
        'mdanalysis>=2.0.0',
        'biobb_structure_checking==3.13.4'
    ],
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "cmip_run = biobb_cmip.cmip.cmip:main",
            "cmip_titration = biobb_cmip.cmip.titration:main",
            "cmip_prepare_structure = biobb_cmip.cmip.prepare_structure:main",
            "cmip_prepare_pdb = biobb_cmip.cmip.prepare_pdb:main",
            "cmip_ignore_residues = biobb_cmip.cmip.ignore_residues:main"
        ]
    },
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix"
    ),
)
