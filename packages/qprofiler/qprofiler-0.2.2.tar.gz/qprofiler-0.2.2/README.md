# qprofiler

**qprofiler** is a Python package that provides an intelligent way to create a data quality profile for your development(train) dataset(s) and save it as a reference to use in creating quality check tests and automatic handling cases for production(test) datasets.

## Table of Contents

- [Installation](#installation)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Contributing](#contributing)
- [Licence](#licence)

## Installation
The source code is currently hosted on GitHub at:
[dprofiler-github](https://github.com/Ezzaldin97/dprofiler)

Binary installers for the latest released version are available at the [PyPi](https://pypi.org/)
```bash
# PyPi
pip install qprofiler
```
## Dependencies

- Polars(>=0.19.0 <0.20.0)
- PyYAML(>=6.0.1 <7.0.0)
- Pathlib(>=1.0 <2.0)
- rumamel.yaml(>=0.17.32 <0.18.0)

## Usage

check the [notebook](notebooks/intro.ipynb) that contains everything about how to use **DataProfiler** module in profiling datasets, and how to use **QTest** module to create quality check tests.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Licence
[MIT](LICENSE)

## New in v0.2.1

- Bug Fixes in QTest.
- Return Messages From Quality Check Tests.