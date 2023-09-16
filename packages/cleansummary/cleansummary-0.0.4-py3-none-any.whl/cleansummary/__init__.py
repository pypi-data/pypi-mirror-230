
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.stats import zscore
import scipy.stats as stats


# Clean Summary class
class CleanSummary():
    
    def __init__(self,data):
        
        self.data = data
    
    def percentage_missing(self):
        
        """Get summary of missing values in the data
        """
        missing = pd.DataFrame(self.data.isnull().sum().reset_index().values, 
                               columns=['variable','missing'])
        missing['%_missing'] = missing['missing']/len(self.data) * 100
        d_types = pd.DataFrame(self.data.dtypes).reset_index()
        d_types.columns = ['variable', 'dtype']
        result = missing.merge(d_types, on='variable')

        return result


    def check_skewness(self, variable):
        
        """Check skewness of a variables
        """

        # calculate skewness
        print("Skewness coefficient: ", self.data[variable].skew())

        # Plot histogram
        plt.figure(figsize=(12,5))
        plt.hist(self.data[variable], bins='auto', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Value',color='blue',fontsize=11)
        plt.ylabel('Frequency',color='blue',fontsize=11)
        plt.title(f'Distribution of {variable}', fontdict={"size":12, "color":"blue"})
        
        # add thousand separator to y-axis labels
        plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        plt.gca().xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))

        plt.xticks(rotation=0)
        plt.grid(True)
        plt.tick_params(axis='x', which='both', labelsize=9, labelcolor='blue')
        plt.tick_params(axis='y', which='both', labelsize=9, labelcolor='blue')
        plt.show()


    def get_statistical_summary(self, variableType=None):
        
        """
        Get statistical summary of numerical varaibles the dataframe"""
                   
        # missing values and data types
        d_types = pd.DataFrame(self.data.dtypes).reset_index()
        d_types.columns = ['variable', 'dtype']
        
        missing = pd.DataFrame(self.data.isnull().sum().reset_index().values, columns=['variable','missing'])
        missing['%_missing'] = missing['missing']/len(self.data) * 100
        d_types_df = pd.DataFrame(self.data.dtypes).reset_index()
        d_types_df.columns = ['variable', 'dtype']
        
        # mapping of data types to human-readable text
        data_type_mapping = {
                                np.dtype('O'): 'Text',
                                np.dtype('int64'): 'Integer',
                                np.dtype('float64'): 'Float',
                                np.dtype('<M8[ns]'): 'Date/Time'
                            }
        # Convert 'dtype' values to human-readable text
        d_types_df['dtype'] = d_types_df['dtype'].map(data_type_mapping)
        
        missing = d_types_df.merge(missing, on='variable')
     
        # descriptive statistics
        summary_statistics = self.data.describe(include="all").T.reset_index().rename(columns={'index':'variable'})

        # calculate unique values in each column
        unique_values = {col: self.data[col].nunique() for col in summary_statistics['variable'].unique()}
        unique_df = pd.DataFrame.from_dict(unique_values, orient='index', 
                        columns=['num_unique']).reset_index().rename(columns={'index':"variable"})
        
        # median
        median_values = {col: self.data[col].median() for col in summary_statistics['variable'].unique() 
                         if self.data[col].dtype!='object'}
        median_df = pd.DataFrame.from_dict(median_values, orient='index', 
                        columns=['median']).reset_index().rename(columns={'index':"variable"})

        # mode
        modal_values = {}
        for col in summary_statistics['variable'].unique():
            modes = self.data[col].mode()
            if not modes.empty:
                modal_values[col] = modes.iat[0]
            else:
                modal_values[col] = None
                
        modal_df = pd.DataFrame.from_dict(modal_values, orient='index', 
                        columns=['mode']).reset_index().rename(columns={'index': 'variable'})

        # skewness
        skewness_values = {col: self.data[col].skew() for col in summary_statistics['variable'].unique() 
                           if self.data[col].dtype not in ['object','datetime64[ns]']}
        skewness_df = pd.DataFrame.from_dict(skewness_values, orient='index', 
                        columns=['skewness']).reset_index().rename(columns={'index':"variable"})

        # number of outliers
        outliers_df = pd.DataFrame(columns=["variable","num_outliers"])
        cols = summary_statistics['variable'].unique()
        for col in cols:
            if self.data[col].dtype in ['object','datetime64[ns]']:
                num_outliers=None
            else:
                z_scores = zscore(self.data[col])
                num_outliers = (abs(z_scores) > 3).sum()
                
            outliers_df = outliers_df.append({'variable': col, 'num_outliers': num_outliers},ignore_index=True)
       
        # check for normality using Shapiro wilk test
        normality_df = pd.DataFrame(columns=["variable","statistic","pValue"])
        for col in self.data.columns:
            if self.data[col].dtype not in ['object','datetime64[ns]']:
            
                stat, p = stats.shapiro(self.data[col])
                normality_df = normality_df.append({"variable":col,"statistic":stat,"pValue":p}, ignore_index=True)
                
        # if p_value > 0.05, then the distribution is normal
        normality_df['normality'] = np.where(normality_df['pValue']>0.05,True,False)
        normality_df.drop(columns=['statistic','pValue'], inplace=True)
    
        # summary
        summary_statistics = missing.merge(summary_statistics, on='variable')
        summary_statistics = summary_statistics.merge(unique_df, on='variable')
        summary_statistics = summary_statistics.merge(median_df, on='variable',how='left')
        summary_statistics = summary_statistics.merge(modal_df, on='variable',how='left')
        summary_statistics = summary_statistics.merge(skewness_df, on='variable', how='left')
        summary_statistics = summary_statistics.merge(outliers_df, on='variable',how='left')
        summary_statistics = summary_statistics.merge(normality_df, on='variable',how='left')
        
        summary_statistics.drop(columns=['unique','top','freq'],inplace=True)
    
        if variableType=='numerical':
            result = summary_statistics[summary_statistics['dtype'].isin(['Integer','Float'])]
            result.dropna(axis=1, inplace=True)
            
        elif variableType=='categorical':
            result = summary_statistics[summary_statistics['dtype'].isin(['Text','Date/Time'])]
            columns_to_drop = ['mean','std','min','25%','50%','75%','max',
                              'median','skewness','num_outliers','normality'] 
            result.drop(columns=columns_to_drop, inplace=True)
            
        else:
            result = summary_statistics
        
        return result