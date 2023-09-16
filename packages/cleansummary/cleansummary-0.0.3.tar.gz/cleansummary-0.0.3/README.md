This is a simple package for exploring pandas dataframe to get the initial statistical summary.


## Getting Started

Installation

`pip install cleansummary`


```
from cleansummary import CleanSummary
cs = CleanSummary(df)
```

### Get proportion of missing data 

`cs.percentage_missing()`


### Get the plot and skewness coefficient of a variable
`cs.check_skewness('variable_name')`


### Get statistical summary

```
cs.get_statistical_summary(variableType=None)

cs.get_statistical_summary(variableType='categorical')

cs.get_statistical_summary(variableType='numerical')
```