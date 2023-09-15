from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="rdfvr",
    version="0.2.0",
    description="RDFVR: RDF Validation Report",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meng6/rdfvr",
    author="Meng Li",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas>=2.0.2", "pyshacl>=0.23.0", "rdflib>=6.3.2", "pygraphviz>=1.11"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.10",
    entry_points='''
        [console_scripts]
        rdfvr=rdfvr:main
    ''',
)