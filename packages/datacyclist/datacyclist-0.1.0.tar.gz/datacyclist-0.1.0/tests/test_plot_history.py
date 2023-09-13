import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch


def create_data():
    df = pd.DataFrame({'power': [1,2,4,5]*25, 
                       'speed': [1]*100,
                       'heart_rate': [1]*100,
                       'cadence': [1]*100, 
                       'year': [1]*100,
                       'wk_no': [1]*100, 
                       'month':[1]*100,
                       'distance': [1]*100, 
                       'activity_no': [1]*100})
    return df

df = create_data()


@patch("matplotlib.pyplot.show")
def test_plot_totals(_):
    """
    Test the function works
    """
    dtc.plot_totals(df)

@patch("matplotlib.pyplot.show")
def test_plot_ratios(_):
    """
    Test the function works
    """
    dtc.plot_ratios(df)