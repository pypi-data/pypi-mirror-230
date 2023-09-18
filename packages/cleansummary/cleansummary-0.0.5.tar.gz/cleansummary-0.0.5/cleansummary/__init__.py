import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import zscore, shapiro

class CleanSummary():
    
    def __init__(self, data):
        """
        Initialize the CleanSummary class with a DataFrame.

        Parameters:
        data (DataFrame): The input DataFrame to be analyzed.

        Raises:
        ValueError: If the input DataFrame is empty.
        """
        if data.empty:
            raise ValueError("Dataframe is empty")
        
        self.data = data
        
    def plot_histogram(self, variable):
        """
        Generate and display a histogram for a given variable.

        Parameters:
        variable (str): The name of the variable to visualize.

        Returns:
        None
        """
        plt.figure(figsize=(12, 5))
        plt.hist(self.data[variable], bins='auto', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value', color='blue', fontsize=11)
        plt.ylabel('Frequency', color='blue', fontsize=11)
        plt.title(f'Distribution of {variable}', fontdict={"size": 12, "color": "blue"})
        plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        plt.gca().xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        plt.xticks(rotation=0)
        plt.grid(True)
        plt.tick_params(axis='x', which='both', labelsize=9, labelcolor='blue')
        plt.tick_params(axis='y', which='both', labelsize=9, labelcolor='blue')
        plt.show()
        
    def check_skewness(self, variable):
        """
        Calculate and display the skewness coefficient for a given variable.

        Parameters:
        variable (str): The name of the variable to analyze.

        Returns:
        A plot
        """
        skewness_coeficient = self.data[variable].skew()
        print("Skewness coefficient: ", round(skewness_coeficient,4))
        return self.plot_histogram(variable)

    def percentage_missing(self):
        """
        Calculate the percentage of missing values for each column in the DataFrame.

        Returns:
        DataFrame: A DataFrame containing columns 'variable', 'missing', and '%_missing'.
        """
        missing = self.data.isnull().sum().reset_index()
        missing.columns = ['variable', 'missing']
        missing['%_missing'] = missing['missing'] / len(self.data) * 100
        d_types = pd.DataFrame(self.data.dtypes).reset_index()
        d_types.columns = ['variable', 'dtype']
        result = missing.merge(d_types, on='variable')
        return result

    def get_statistical_summary(self, variableType=None):
        """
        Generate a statistical summary of the DataFrame.

        Parameters:
        variableType (str, optional): Type of variables to include in the summary ('numerical', 'categorical', or None).

        Returns:
        DataFrame: A DataFrame containing the statistical summary.
        """
        if self.data.empty:
            raise ValueError("Dataframe is empty")
        
        data_type_mapping = {
            np.dtype('O'): 'Text',
            np.dtype('int64'): 'Integer',
            np.dtype('float64'): 'Float',
            np.dtype('<M8[ns]'): 'Date/Time',
            np.dtype('bool'): 'Boolean'
        }
        
        def get_modal_values(col):
            modes = self.data[col].mode()
            return modes.iat[0] if not modes.empty else None
        
        summary_statistics = self.data.describe(include="all").T.reset_index().rename(
            columns={'index': 'variable'})

        summary_statistics['dtype'] = summary_statistics['variable'].apply(lambda col: data_type_mapping.get(self.data[col].dtype, None))
        
        summary_statistics['%_missing'] = (self.data.isnull().sum() / len(self.data) * 100).values
        summary_statistics['num_unique'] = self.data.nunique().values
        summary_statistics['mode'] = summary_statistics['variable'].apply(get_modal_values)
    
        numerical_columns = self.data.select_dtypes(include=['int64', 'float64']).columns

        median_values = {col: self.data[col].median() for col in numerical_columns}
        summary_statistics['median'] = summary_statistics['variable'].map(median_values)

        skewness_values = {col: self.data[col].skew() for col in numerical_columns}
        summary_statistics['skewness_coefficient'] = summary_statistics['variable'].map(skewness_values)

        STDEV_THRESHOLD = 3

        def count_outliers(col):
            if self.data[col].dtype in ['object', 'datetime64[ns]']:
                return None
            z_scores = zscore(self.data[col])
            return (abs(z_scores) > STDEV_THRESHOLD).sum()

        summary_statistics['num_outliers'] = summary_statistics['variable'].apply(count_outliers)

        SIGNIFICANCE_LEVEL = 0.05

        def check_normality(col):
            if self.data[col].dtype not in ['object', 'datetime64[ns]']:
                stat, p = shapiro(self.data[col])
                return p > SIGNIFICANCE_LEVEL
            return False

        summary_statistics['normality'] = summary_statistics['variable'].apply(check_normality)

        summary_statistics.drop(columns=['unique', 'top', 'freq'], inplace=True)

        if variableType == 'numerical':
            result = summary_statistics[summary_statistics['dtype'].isin(['Integer', 'Float'])]
            result.dropna(axis=1, inplace=True)

        elif variableType == 'categorical':
            result = summary_statistics[summary_statistics['dtype'].isin(['Text', 'Date/Time', 'Boolean'])]
            columns_to_drop = ['mean', 'std', 'min', '25%', '50%', '75%', 'max',
                               'median', 'skewness_coefficient', 'num_outliers', 'normality']
            result.drop(columns=columns_to_drop, inplace=True)

        else:
            result = summary_statistics
            
        numeric_columns = ['mean', 'std', 'min', '25%', '50%', '75%', 'max',
                            'median', 'skewness_coefficient']
        
        for col in numeric_columns:
            if col in result.columns:
                result[col] = result[col].apply(lambda x: round(float(x), 4))

        return result
