import fitdecode

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Union, Optional,Tuple

#thanks to this script https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_fit.py

POINTS_COLUMN_NAMES = ['latitude', 'longitude', 'lap', 'altitude', 'timestamp', 'heart_rate', 
                       'cadence', 'speed', 'power','temperature', 'left_power_phase', 'left_power_phase_peak']

# The names of the columns we will use in our laps DataFrame. 
LAPS_COLUMN_NAMES = ['lap', 'start_time', 'total_distance', 'total_elapsed_time', 
                     'total_strokes', 'total_work', 'total_calories', 'time_standing',
                     'avg_speed', 'max_speed',
                     'avg_power', 'max_power',
                     'total_ascent', 'total_descent',
                     'avg_cadence', 'max_cadence',
                     'avg_temperature', 'max_temperature',
                     'normalized_power', 
                     'max_heart_rate', 'avg_heart_rate', 
                     'avg_left_power_phase', 'avg_left_power_phase_peak']


def get_fit_lap_data(frame: fitdecode.records.FitDataMessage) -> Dict[str, Union[float, datetime, timedelta, int]]:
    """Extract some data from a FIT frame representing a lap and return
    it as a dict.
    """
    
    data: Dict[str, Union[float, datetime, timedelta, int]] = {}
    
    for field in LAPS_COLUMN_NAMES[1:]:  # Exclude 'number' (lap number) because we don't get that
                                        # from the data but rather count it ourselves
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    
    return data


def get_fit_point_data(frame: fitdecode.records.FitDataMessage) -> Optional[Dict[str, Union[float, int, str, datetime]]]:
    """Extract some data from an FIT frame representing a track point
    and return it as a dict.
    """
    
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    if not (frame.has_field('position_lat') and frame.has_field('position_long')):
        # Frame does not have any latitude or longitude data. We will ignore these frames in order to keep things
        # simple, as we did when parsing the TCX file.
        return None
    else:
        data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
        data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
    
    for field in POINTS_COLUMN_NAMES[3:]:
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    
    return data


def crop_activity(data, minutes=10):
    activity_start = data['timestamp'].min()
    activity_end = data['timestamp'].max()
    
    cropped = data.loc[(data['timestamp'] > activity_start + pd.Timedelta(minutes=minutes)) & 
                       (data['timestamp'] < activity_end - pd.Timedelta(minutes=minutes)), ]
    
    return cropped.reset_index(drop=True)
    

def get_dataframes(fname: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Takes the path to a FIT file (as a string) and returns two Pandas
    DataFrames: one containing data about the laps, and one containing
    data about the individual points.
    """

    points_data = []
    laps_data = []
    lap_no = 1
    with fitdecode.FitReader(fname) as fit_file:
        for frame in fit_file:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                if frame.name == 'record':
                    single_point_data = get_fit_point_data(frame)
                    if single_point_data is not None:
                        single_point_data['lap'] = lap_no
                        points_data.append(single_point_data)
                elif frame.name == 'lap':
                    single_lap_data = get_fit_lap_data(frame)
                    single_lap_data['lap'] = lap_no
                    laps_data.append(single_lap_data)
                    lap_no += 1
    
    # Create DataFrames from the data we have collected. If any information is missing from a particular lap or track
    # point, it will show up as a null value or "NaN" in the DataFrame.
    
    laps_df = pd.DataFrame(laps_data, columns=LAPS_COLUMN_NAMES)
    points_df = pd.DataFrame(points_data, columns=POINTS_COLUMN_NAMES)
    
    # more privacy
    points_df = crop_activity(points_df)
    
    return laps_df, points_df



