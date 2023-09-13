import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch


def create_data():
    df = pd.DataFrame({'activity_no': [1, 1, 1, 1, 1, 1], 
                       'distance': [0,5,5, 5, 5, 1], 
                       'time_elapsed': [0, 1, 2, 3, 4, 5],
                       'time_diff': [1,1,1, 1, 1, 1],
                       'activity_distance': [21]*6, 
                       'distance_covered': [0,5,10,15,20,21], 
                       'year': [1,1,1, 1, 1, 1], 
                       'month': [1,1,1 ,1, 1, 1] })
    return df

df = create_data()


@pytest.mark.parametrize("col", ['activity_no', 'distance', 'time_diff', 'activity_distance', 
                'time_elapsed', 'distance_covered', 'year', 'month'])
def test_missing_columns(col):
    """
    Test if a KeyError is raised if any of the required columns is missing
    """
    data = df.copy()
    del data[col]
    with pytest.raises(KeyError):
        pc = dtc.FastestSegment(data, 1)


def test_toprides_io():
    """
    Test if top_rides is returning a dataframe with the right columns
    """
    fs = dtc.FastestSegment(df, 1)
    top10, monthly = fs.top_rides()
    diff = {'time', 'activity_no', 'year', 'month'} - set(top10.columns)
    assert len(list(diff)) == 0
    diff = {'time', 'activity_no', 'year', 'month'} - set(monthly.columns)
    assert len(list(diff)) == 0
    
    
def test_toprides():
    """
    Test it returns the right values
    """
    tmp = df.copy()
    tmp['activity_no'] = 2
    tmp = pd.concat([df, tmp], ignore_index=True)
    fs = dtc.FastestSegment(tmp, 1)
    top10, monthly = fs.top_rides()
    assert top10['activity_no'].nunique() == 2
    
    
def test_findwindow():
    """
    Test the find_window method, checking the numbers are as expected
    """
    fs = dtc.FastestSegment(df, 20)
    fastest_time, time_start, time_end, activity_no = fs.find_window()
    assert fastest_time == 4
    assert time_start == 1
    assert time_end == 4  
    assert activity_no == 1
    
    
@patch("matplotlib.pyplot.show")
def test_plot_bestrides(_):
    """
    Test if plot_best_rides works
    """
    fs = dtc.FastestSegment(df, 20)
    _, _ = fs.top_rides()
    fs.plot_best_rides()
    
    
@patch("matplotlib.pyplot.show")
def test_plot_bestrides_norides(_):
    """
    Test if plot_best_rides works when best_rides has not been called already
    """
    fs = dtc.FastestSegment(df, 20)
    fs.plot_best_rides()
    
