import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest


def create_data():
    df = pd.DataFrame({'timestamp': pd.date_range(start="2023-01-01", periods=11, freq='S'),
                       'time_elapsed': np.arange(0,11),
                       'power': [0,0,1,1,1,1,2,2,2,2,3], 
                       'heart_rate': [0,0,1,1,1,1,2,2,2,2,3], 
                       'cadence': [0,0,1,1,1,1,2,2,2,2,3]})
    return df

df = create_data()

@pytest.mark.parametrize("col", ['timestamp', 'power', 'cadence', 'heart_rate', 'time_elapsed'])
def test_missing_columns(col):
    """
    Test if a KeyError is raised if any of the required columns is missing
    """
    data = df.copy()
    del data[col]
    with pytest.raises(KeyError):
        pc = dtc.PowerCurve()
        pc.calculate_curve(data)


@pytest.mark.parametrize("sec", [1,2,5,10,20,30,60,120,300,600,1200,3600,7200,18000])
def test_curves_attributes(sec):
    """
    Test the attributes are there for each duration and the initialization worked
    """
    pc = dtc.PowerCurve()
    attr = getattr(pc, f'sec_{sec}')
    assert attr['activity_best'] == 0
    assert attr['activity_HR'] == 0
    assert attr['activity_cadence'] == 0
    assert attr['alltime_best'] == 0
    assert attr['alltime_HR'] == 0
    assert attr['alltime_cadence'] == 0
    
    
def test_get_activity_curve():
    """
    Test the method returns a dataframe with the info we need
    """
    pc = dtc.PowerCurve()
    res = pc.get_activity_curve()
    diff = {'Time', 'Activity Curve', 'Best Curve', 'Activity HR', 
            'HR Best Curve', 'Activity Cadence', 'Cadence Best Curve'} - set(res.columns)
    assert len(list(diff)) == 0
    assert res.shape[0] == 14  # the 14 time intervals of the curve


    
def test_curve_calculation():
    """
    Test the results are actually correct
    """
    pc = dtc.PowerCurve()
    pc.calculate_curve(df)
    assert pc.sec_1['activity_best'] == 3
    assert pc.sec_2['activity_best'] == 2.5
    assert pc.sec_5['activity_best'] == 2.2
    assert pc.sec_10['activity_best'] == 1.5
    assert pc.sec_1['activity_HR'] == 3
    assert pc.sec_2['activity_HR'] == 2.5
    assert pc.sec_5['activity_HR'] == 2.2
    assert pc.sec_10['activity_HR'] == 1.5
    assert pc.sec_1['activity_cadence'] == 3
    assert pc.sec_2['activity_cadence'] == 2.5
    assert pc.sec_5['activity_cadence'] == 2.2
    assert pc.sec_10['activity_cadence'] == 1.5
    
    
def test_curve_missing_seconds():
    """
    Test the behavior when a second is missing
    We use forward fill
    """
    data = df.copy()
    data.loc[data.index[3], data.columns] = np.nan
    pc = dtc.PowerCurve()
    pc.calculate_curve(df)
    # Nothing should change
    assert pc.sec_1['activity_best'] == 3
    assert pc.sec_2['activity_best'] == 2.5
    assert pc.sec_5['activity_best'] == 2.2
    assert pc.sec_10['activity_best'] == 1.5
    
    
    