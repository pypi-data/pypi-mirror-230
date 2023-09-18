import unittest
import pandas as pd
import numpy as np
import logging
from cleansummary import CleanSummary
import matplotlib.pyplot as plt
import warnings

# Set the Matplotlib logging level to WARNING
logging.getLogger('matplotlib').setLevel(logging.WARNING)

class TestCleanSummary(unittest.TestCase):

    def setUp(self):
        # Sample DataFrame for testing
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [None, 7, 8, None, 10],
            'C': ['queen', 'king', 'duke', 'duchess', 'monarch'],
            'D': [None, None, None, None, None]
        })
        self.clean_summary = CleanSummary(data)
        logging.basicConfig(level=logging.DEBUG)

    def test_percentage_missing(self):
        # Test the result of percentage_missing method
        result = self.clean_summary.percentage_missing()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue('variable' in result.columns)
        self.assertTrue('missing' in result.columns)

    def test_check_skewness(self):
        variable = 'B'
        self.clean_summary.check_skewness(variable)
        # Check if a figure was created
        self.assertIsNotNone(plt.gcf())

    def test_get_statistical_summary(self):
        # Test if the result is a dataframe
        result = self.clean_summary.get_statistical_summary()
        self.assertIsInstance(result, pd.DataFrame)

    def test_get_statistical_summary_numerical(self):
        # Test if the result is a dataframe
        result = self.clean_summary.get_statistical_summary(variableType='numerical')
        self.assertIsInstance(result, pd.DataFrame)

    def test_get_statistical_summary_categorical(self):
        # Test if the result is a dataframe
        result = self.clean_summary.get_statistical_summary(variableType='categorical')
        self.assertIsInstance(result, pd.DataFrame)
                
if __name__ == '__main__':
    unittest.main()
