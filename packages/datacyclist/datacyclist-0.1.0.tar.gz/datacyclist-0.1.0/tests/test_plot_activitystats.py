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
                       'longitude': [1]*100, 
                       'latitude': [1]*100, 
                       'Power_Training_zone': [1]*100,
                       'HR_Training_zone': [1]*100, 
                       'distance_covered': [1]*100})
    return df

df = create_data()

@pytest.mark.parametrize("col", ['power', 'heart_rate', 'cadence', None])
@patch("matplotlib.pyplot.show")
def test_plot_activitystats_nocol_nocurves(_, col):
    """
    Test if the works if non-essential columns are missing
    """
    tmp = df.copy()
    if col is not None:
        tmp[col] = np.nan
    dtc.ActivityStats(tmp, power_curve=None)

    
@pytest.mark.parametrize("col", ['power', 'heart_rate', 'cadence', 
               'speed', 'longitude', 'latitude', 
                'Power_Training_zone', 'HR_Training_zone', 
                'distance_covered'])
def test_missing_columns(col):
    """
    Test if a KeyError is raised if any of the required columns is missing
    """
    data = df.copy()
    del data[col]
    with pytest.raises(KeyError):
        dtc.ActivityStats(data)
