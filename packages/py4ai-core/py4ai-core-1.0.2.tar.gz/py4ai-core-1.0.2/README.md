py4ai core
====

[![PyPI](https://img.shields.io/pypi/v/py4ai-core.svg)](https://pypi.python.org/pypi/py4ai-core)
[![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.python.org/pypi/py4ai-core)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://py4ai.github.io/py4ai-core/)
![Python package](https://github.com/NicolaDonelli/py4ai-core/workflows/CI%20-%20Build%20and%20Test/badge.svg)

--------------------------------------------------------------------------------


A Python library defining data structures optimized for machine learning pipelines 


## What is it ?
**py4ai-core** is a Python package with modular design that provides powerful abstractions to build data 
ingestion pipelines and run end to end machine learning pipelines. 
The library offers lightweight object-oriented interface to MongoDB as well as Pandas based data structures. 
The aim of the library is to provide extensive support for developing machine learning based applications 
with a focus on practicing clean code and modular design. 

## Features
Some cool features that we are proud to mention are: 

### Logging 
1. configFromFiles: utility function to configure loggers according to configuration files, giving options to capture warnings and to define which logger to use to capture errors.
2. WithLogging: Base class setting up the `logger` property defining a logger named according to the class to be used in descendant classes.

### Configurations
Offers a unified framework to parse and store yaml configuration files: 
1. get_confs_in_path: Retrieve all configuration files from system path, with given extension.
2. merge_confs : merge given configuration files. 
3. BaseConfig : Basic configuration class. This class implements utility methods to retrieve configuration sub-levels and values. An instance of this class can be updated merging other instances of the same class.
4. Some pre-implemented configuration classes for some common use cases like: FileSystemConfig, LoggingConfig, MongoConfig and many more.

## Installation
From pypi server
```
pip install py4ai-core
```

From source
```
git clone https://github.com/NicolaDonelli/py4ai-core
cd py4ai-core
make install
```

## Tests 
```
make tests
```

## Checks 
To run predefined checks (unit-tests, linting checks, formatting checks and static typing checks):
```
make checks
```

## How to contribute ? 

We are very much willing to welcome any kind of contribution whether it is bug report, bug fixes, contributions to the 
existing codebase or improving the documentation. 

### Where to start ? 
Please look at the [Github issues tab](https://github.com/NicolaDonelli/py4ai-core/issues) to start working on open 
issues 

### Contributing to py4ai-core 
Please make sure the general guidelines for contributing to the code base are respected
1. [Fork](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) the py4ai-core repository. 
2. Create/choose an issue to work on in the [Github issues page](https://github.com/NicolaDonelli/py4ai-core/issues). 
3. [Create a new branch](https://docs.github.com/en/get-started/quickstart/github-flow) to work on the issue. 
4. Commit your changes and run the tests to make sure the changes do not break any test. 
5. Open a Pull Request on Github referencing the issue.
6. Once the PR is approved, the maintainers will merge it on the main branch.