import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datacyclist.utils import plot_frame


def plot_totals(data):
    """
    This function plots the total distance, average power, speed, and cadence per week.
    
    :param data: pd.DataFrame with distance, power, speed, and cadence data over time
    """
    fig, ax = plt.subplots(4, 1, figsize=(15, 20), facecolor='#292525')
    fig.subplots_adjust(top=0.95)
    fig.suptitle(f' Analysis', fontsize=18, color='w')
    
    (data.groupby(['year', 'wk_no'])['distance'].sum() / 1000).plot(ax=ax[0], kind='bar')
    data.groupby(['year', 'wk_no'])['power'].mean().plot(kind='bar', ax=ax[1], color='#ECDE15')
    (data.groupby(['year', 'wk_no'])['speed'].mean()*3.6).plot(kind='bar', ax=ax[2])
    data.groupby(['year', 'wk_no'])['cadence'].mean().plot(kind='bar', ax=ax[3], color='#27B012')
        
    ax[0].set_title('Distance', fontsize=14, color='w')
    ax[1].set_title('Power', fontsize=14, color='w')
    ax[2].set_title('Speed', fontsize=14, color='w')
    ax[3].set_title('Cadence', fontsize=14, color='w')
    
    for axes in ax:
        axes = plot_frame(axes)
        axes.set_xlabel('')
        axes.set_xticks([])
        
    plt.show()

    
def plot_ratios(data):
    """
    This function plots a series of scatter plots of mean power, cadence, speed and heart rate per activity
    For example, mean speed vs mean power
    
    :param data: pd.DataFrame with data of power, cadence, speed, and heart rate per activity
    """
    fig, ax = plt.subplots(3, 2, figsize=(15, 15), facecolor='#292525')
    fig.subplots_adjust(top=0.95)
    fig.suptitle(f'Mean Ratios by activity', fontsize=18, color='w')
    
    df = data.groupby('activity_no', as_index=False)[['power', 'cadence', 'speed', 'heart_rate']].mean()
    df['speed'] = df['speed'] * 3.6
    dates = data[['activity_no', 'year', 'month']].drop_duplicates()
    df = pd.merge(df, dates, on='activity_no', how='left')
        
    sns.scatterplot(df, x='power', y='speed', ax=ax[0][0])
    sns.scatterplot(df, x='power', y='cadence', ax=ax[0][1])
    sns.scatterplot(df, x='power', y='heart_rate', ax=ax[1][0])
    sns.scatterplot(df, x='cadence', y='heart_rate', ax=ax[1][1])
    sns.scatterplot(df, x='cadence', y='speed', ax=ax[2][0])
    sns.scatterplot(df, x='heart_rate', y='speed', ax=ax[2][1])

    ax[0][0] = plot_frame(ax[0][0])
    ax[0][1] = plot_frame(ax[0][1])
    ax[1][0] = plot_frame(ax[1][0])
    ax[1][1] = plot_frame(ax[1][1])
    ax[2][0] = plot_frame(ax[2][0])
    ax[2][1] = plot_frame(ax[2][1])
        
    plt.show()
