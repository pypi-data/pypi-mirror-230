## Get Started

Source code: [GitHub Repository](https://github.com/fonyango/cleansummary.git)

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