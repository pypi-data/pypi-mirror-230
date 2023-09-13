import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from datacyclist.utils import plot_frame



class ActivityStats():
    """
    This class plots all the available stats of an activity when initialized
    The basic plot is a plot of path and the speed (averaged over 10 seconds)
    It also displays a summary of the ride in the form of a table
    
    If power data is available, it will be in a plot (averaged over 20 seconds). Moreover, it will plot
    a pie chart with the time in each power zone, the power curve of this activity and of all time (if available),
    and a histogram with the 25 Watts distribution. At last, the power data will be also in the summary table
    
    If heart rate data is available, it will be in a plot (averaged over 5 seconds). Moreover, it will plot
    a pie chart with the time in each heart rate zone, and the data will be displayed in the summary table.
    
    If cadence data is available, it will be in a plot (averaged over 20 seconds). The data will be also
    displayed in the summary table.
    
    The size of the plot is dynamic, depending on the available data
    
    :param data: pd.Dataframe with columns `power`, `heart_rate`, `cadence`, 
               `speed`, `longitude`, `latitude`, 
                `Power_Training_zone`, `HR_Training_zone`, 
                `distance_covered`.
                
    :param power_curve: PowerCurve object, if provided and power data is present, it will be plotted.
    """
    def __init__(self, data, power_curve=None):
        self.data = data
        self._check_data()
        self.power_curve = power_curve
        self.stat_dict = {'power': 0, 'heart_rate': 0, 'cadence': 0}
        self._update_dict()
        self._make_fig()
        self._plot_path()
        self._plot_speed()
        self._plot_power()
        self._plot_hr()
        self._plot_cadence()
        self._plot_power_curve()
        self._plot_power_dist()
        self._plot_powerzone()
        self._plot_hrzone()
        self._plot_summary()
        plt.show()
        
        
    def _check_data(self):
        diff = {'power', 'heart_rate', 'cadence', 
               'speed', 'longitude', 'latitude', 
                'Power_Training_zone', 'HR_Training_zone', 
                'distance_covered'} - set(self.data.columns)
        if len(list(diff)) > 0:
               raise KeyError(f'Missing columns required: {diff}')
                
        
    def _update_dict(self):
        for stat in ['power', 'heart_rate', 'cadence']:
            if self.data[stat].notna().any():
                self.stat_dict[stat] = 1
        
    def _make_fig(self):
        self.fig = plt.figure(figsize=(15, 10 + 
                                       5 * self.stat_dict['power'] + 
                                       5 * self.stat_dict['heart_rate'] + 
                                       5 * self.stat_dict['cadence'] + 
                                       5 * max(self.stat_dict['power'], self.stat_dict['heart_rate']) ), 
                              facecolor='#292525')
        
        gs = GridSpec(4 + 2*self.stat_dict['power'] + 
                      2*self.stat_dict['heart_rate'] + 
                      2*self.stat_dict['cadence'] + 
                      2*max(self.stat_dict['power'], self.stat_dict['heart_rate']), 4, 
                      figure=self.fig)
        self.path = self.fig.add_subplot(gs[:2, :2])
        self.sum = self.fig.add_subplot(gs[0, 2:])
        self.speed = self.fig.add_subplot(gs[2:4, :])
        if self.stat_dict['power'] == 1:
            self.power_zone = self.fig.add_subplot(gs[1, 2])
            self.power = self.fig.add_subplot(gs[4:6, :])
            if self.power_curve is not None:
                self.power_curve_pl = self.fig.add_subplot(gs[(6+
                                                            2*self.stat_dict['heart_rate']+
                                                            2*self.stat_dict['cadence']):(8
                                                           +2*self.stat_dict['heart_rate']
                                                           +2*self.stat_dict['cadence']), :2])
            self.power_dist = self.fig.add_subplot(gs[(6+
                                                        2*self.stat_dict['heart_rate']+
                                                        2*self.stat_dict['cadence']):(8
                                                       +2*self.stat_dict['heart_rate']
                                                       +2*self.stat_dict['cadence']), 2:])
        if self.stat_dict['heart_rate'] == 1:
            self.hr_zone = self.fig.add_subplot(gs[1, 3])
            self.hr = self.fig.add_subplot(gs[4+2*self.stat_dict['power']:6+2*self.stat_dict['power'], :])
        if self.stat_dict['cadence'] == 1:
            self.cadence = self.fig.add_subplot(gs[(4+
                                                      2*self.stat_dict['power']+
                                                      2*self.stat_dict['heart_rate']):(6+
                                                      2*self.stat_dict['power']+
                                                      2*self.stat_dict['heart_rate']), :])

    def _plot_path(self):
        sns.scatterplot(data=self.data, 
                        x='longitude', y='latitude', c='red', 
                        legend=False,
                        ax=self.path)
        self.path = plot_frame(self.path)
        self.path.set_xlabel('')
        self.path.set_ylabel('')
        self.path.set_xticks([])
        self.path.set_yticks([])
        
        
    def _smooth_series(self, series, kernel_size=10):
#         kernel = np.ones(kernel_size) / kernel_size
#         smooth = np.convolve(series, kernel, mode='same')
        smooth = series.rolling(window=kernel_size, min_periods=kernel_size).mean()
        return smooth
        
    def _plot_speed(self):
        tmp = pd.Series(self._smooth_series(self.data['speed'] *3.6))
        mean_speed = (self.data['speed'] *3.6).mean()
        tmp.plot(ax=self.speed, color='w')
        self.speed.axhline(mean_speed, color='w', linestyle='--', alpha=0.7)
        self.speed = plot_frame(self.speed)
        self.speed.set_xticks([])
        self.speed.set_ylim((0, (self.data['speed'] *3.6).max()+1))
        self.speed.set_title('Speed', fontsize=14, color='w')

        
    def _plot_power(self):
        if self.stat_dict['power'] == 1:
            tmp = pd.Series(self._smooth_series(self.data['power'], kernel_size=20))
            mean_power = self.data['power'].mean()
            tmp.plot(ax=self.power, color='#ECDE15')
            self.power.axhline(mean_power, color='#ECDE15', linestyle='--', alpha=0.7)
            self.power = plot_frame(self.power)
            self.power.set_xticks([])
            self.power.set_ylim((0, (tmp.max()+10)))
            self.power.set_title('Power', fontsize=14, color='w')
            
    def _plot_hr(self):
        if self.stat_dict['heart_rate'] == 1:
            tmp = pd.Series(self._smooth_series(self.data['heart_rate'], kernel_size=5))
            mean_hr = self.data['heart_rate'].mean()
            tmp.plot(ax=self.hr, color='#EC1515')
            self.hr.axhline(mean_hr, color='#EC1515', linestyle='--', alpha=0.7)
            self.hr = plot_frame(self.hr)
            self.hr.set_xticks([])
            self.hr.set_ylim((50, (tmp.max()+10)))
            self.hr.set_title('Heart Rate', fontsize=14, color='w')
            
    def _plot_cadence(self):
        if self.stat_dict['cadence'] == 1:
            tmp = pd.Series(self._smooth_series(self.data['cadence'], kernel_size=20))
            mean_cad = self.data['cadence'].mean()
            tmp.plot(ax=self.cadence, color='#27B012')
            self.cadence.axhline(mean_cad, color='#27B012', linestyle='--', alpha=0.7)
            self.cadence = plot_frame(self.cadence)
            self.cadence.set_xticks([])
            self.cadence.set_ylim((0, (tmp.max()+10)))
            self.cadence.set_title('Cadence', fontsize=14, color='w')
            
    def _plot_power_curve(self):
        if self.stat_dict['power'] == 1 and self.power_curve is not None:
            self.power_curve.calculate_curve(self.data)
            b = self.power_curve.get_activity_curve()
            b['Best Curve'].plot(ax=self.power_curve_pl, label='Best Curve')
            b['Activity Curve'].plot(ax=self.power_curve_pl, label='Activity Curve')
            self.power_curve_pl = plot_frame(self.power_curve_pl)
            self.power_curve_pl.set_xticklabels(['', '1s', '5s', '20s', '1m', '5m', '20m', '2h'])
            self.power_curve_pl.set_title('Power Curve', fontsize=14, color='w')
            self.power_curve_pl.legend(loc='upper right', facecolor='#292525', framealpha=1, labelcolor='w')
            
    def _plot_power_dist(self):
        if self.stat_dict['power'] == 1:
            sns.histplot(data=self.data['power'], binwidth=25, kde=True, ax=self.power_dist)
            self.power_dist = plot_frame(self.power_dist)
            self.power_dist.set_xlabel('')
            self.power_dist.set_ylabel('')
            self.power_dist.set_yticks([])
            self.power_dist.set_title('Power Distribution', fontsize=14, color='w')
            
            
    def _plot_powerzone(self):
        if self.stat_dict['power'] == 1:
            data = self.data['Power_Training_zone'].value_counts().sort_index().values
            wedges, texts = self.power_zone.pie(data, wedgeprops=dict(width=0.5), startangle=-40)
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-"),
                      bbox=bbox_props, zorder=0, va="center")
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = f"angle,angleA=0,angleB={ang}"
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                self.power_zone.annotate(i+1, xy=(x, y), xytext=(1.3*np.sign(x), 1.2*y),
                            horizontalalignment=horizontalalignment, **kw)
            self.power_zone = plot_frame(self.power_zone)
            self.power_zone.set_title('Power Zones', fontsize=14, color='w')
            
            
    def _plot_hrzone(self):
        if self.stat_dict['heart_rate'] == 1:
            data = self.data['HR_Training_zone'].value_counts().sort_index().values
            wedges, texts = self.hr_zone.pie(data, wedgeprops=dict(width=0.5), startangle=-40)
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-"),
                      bbox=bbox_props, zorder=0, va="center")
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = f"angle,angleA=0,angleB={ang}"
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                self.hr_zone.annotate(i+1, xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                            horizontalalignment=horizontalalignment, **kw)
            self.hr_zone = plot_frame(self.hr_zone)
            self.hr_zone.set_title('HR Zones', fontsize=14, color='w')
            
            
    def _plot_summary(self):
        data_rows = ['speed'] + self.stat_dict['power'] * ['power'] + self.stat_dict['heart_rate'] * ['heart_rate'] + self.stat_dict['cadence'] * ['cadence']
        rows_names = ['Speed'] + self.stat_dict['power'] * ['Power'] + self.stat_dict['heart_rate'] * ['HR'] + self.stat_dict['cadence'] * ['Cadence'] + ['Distance']
        data = self.data.copy()
        distance = {'mean': '', 'max': round(data.distance_covered.max() / 1000, 2)}
        data['speed'] = data['speed'] * 3.6
        data = round(data[data_rows].agg(['mean', 'max']).T,2 )
        data.loc['Distance'] = distance
        self.sum.table(cellText=data.values, colLabels=['Avg.', 'Max'], loc='center', rowLabels=rows_names, colLoc='center', colWidths=[0.1,0.1])
        self.sum = plot_frame(self.sum)
        self.sum.axis('off')
        self.sum.axis('tight')
        