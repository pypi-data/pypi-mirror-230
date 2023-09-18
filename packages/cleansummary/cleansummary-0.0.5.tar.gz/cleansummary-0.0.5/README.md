# cleansummary

[![GitHub License](https://img.shields.io/github/license/fonyango/cleansummary)](https://github.com/fonyango/cleansummary/blob/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/cleansummary)](https://pypi.org/project/cleansummary/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cleansummary)](https://pypi.org/project/cleansummary/)

This is a simple python package for exploring pandas dataframe to get the initial statistical summary.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Use pip directly

`pip install cleansummary`

Or install from source

```
git clone https://github.com/fonyango/cleansummary.git
cd cleansummary
pip install .
```

## Usage

Import the library

`from cleansummary import CleanSummary`

Instantiate the library using a dataframe

`cs = CleanSummary(df)`

Get proportion of missing data 

`cs.percentage_missing()`

Get the plot and skewness coefficient of a variable

`cs.check_skewness('variable_name')`

Get statistical summary

```
cs.get_statistical_summary(variableType=None)

cs.get_statistical_summary(variableType='categorical')

cs.get_statistical_summary(variableType='numerical')
```
## Contributing

Let's make it better! If you would like to contribute to this project, please follow these steps:

- Fork the repository on GitHub.

- Clone the forked repository to your local machine.

- Create a new branch for your feature or bug fix: `git checkout -b feature-name`

- Make your changes and commit them with descriptive commit messages.

- Push your changes to your fork on GitHub: git push origin feature-name

- Create a pull request from your forked repository to this repository.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/fonyango/cleansummary/blob/master/license.txt) file for details.



