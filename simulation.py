import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
import matplotlib.pyplot as plt

class StudyParticipant:

    def __init__(self):
        self.progress_time = None
        self.death_time = None
        self.censor_time = None
    
    def progress(self, t):
        self.progress_time = t

    def die(self, t):
        self.death_time = t

    def censor(self, t):
        self.censor_time = t


class Study:

    def __init__(
            self, n, 
            h_progression_treatment, h_death_treatment, h_censor_treatment,  h_death_given_progression_treatment, h_death_given_censor_treatment,
            h_progression_control, h_death_control, h_censor_control, h_death_given_progression_control, h_death_given_censor_control
            ):
        self.t = 0
        self.h_progression_t = h_progression_treatment
        self.h_death_t = h_death_treatment
        self.h_censor_t = h_censor_treatment
        self.h_death_given_progression_t = h_death_given_progression_treatment
        self.h_death_given_censor_t = h_death_given_censor_treatment
        self.h_progression_c = h_progression_control
        self.h_death_c = h_death_control
        self.h_censor_c = h_censor_control
        self.h_death_given_progression_c = h_death_given_progression_control
        self.h_death_given_censor_c = h_death_given_censor_control

        self.treatment_group = [StudyParticipant() for x in range(n)]
        self.control_group = [StudyParticipant() for x in range(n)]
        self.complete = False

    def get_treatment_group(self):
        return self.treatment_group
    
    def get_control_group(self):
        return self.control_group
    
    def check_complete(self):
        for participant in self.treatment_group + self.control_group:
            if not participant.death_time:
                return False

        return True

    def simulate_period(self):

        self.t += 1

        def draw_events(t, participant, h_p, h_d, h_c, h_d_g_p, h_d_g_c):
            has_progression = False
            has_death = False 
            has_censor = False

            if participant.death_time:
                return
            
            if participant.censor_time: 
                has_death = random.choices([True, False], weights = [h_d_g_c, 1-h_d_g_c], k=1)[0]

            elif participant.progress_time:
                has_death = random.choices([True, False], weights = [h_d_g_p, 1-h_d_g_p], k=1)[0]

            else:
                has_progression = random.choices([True, False], weights = [h_p, 1-h_p], k=1)[0]
                has_death = random.choices([True, False], weights = [h_d, 1-h_d], k=1)[0]
                has_censor = random.choices([True, False], weights = [h_c, 1-h_c], k=1)[0]

            if has_death:
                participant.die(t)
                return

            if has_censor:
                participant.censor(t)
                return

            if has_progression:
                participant.progress(t)

            
        for participant in self.treatment_group:
            draw_events(self.t, participant, self.h_progression_t, self.h_death_t, self.h_censor_t, self.h_death_given_progression_t, self.h_death_given_censor_t)
        
        for participant in self.control_group:
            draw_events(self.t, participant, self.h_progression_c, self.h_death_c, self.h_censor_c, self.h_death_given_progression_c, self.h_death_given_censor_c)

        self.complete = self.check_complete()



def simulate_trial(n, h_progression_t, h_death_t, h_censor_t, h_death_given_progression_t, h_death_given_censor_t, h_progression_c, h_death_c, h_censor_c, h_death_given_progression_c, h_death_given_censor_c, plot=False):
    
    study = Study(
        n=n,
        h_progression_treatment=h_progression_t,
        h_death_treatment=h_death_t,
        h_censor_treatment=h_censor_t,
        h_death_given_progression_treatment=h_death_given_progression_t,
        h_death_given_censor_treatment=h_death_given_censor_t,
        h_progression_control=h_progression_c,
        h_death_control=h_death_c,
        h_censor_control=h_censor_c,
        h_death_given_progression_control=h_death_given_progression_c,
        h_death_given_censor_control = h_death_given_censor_c
    )

    while not study.complete:
        study.simulate_period()

    data_treatment = [{
        'participant': f't_{id}', 
        'group': 1, 
        't_progression': participant.progress_time,
        't_death': participant.death_time,
        't_censor': participant.censor_time,
        } for id, participant in enumerate(study.get_treatment_group())
    ]
    data_control = [{
        'participant': f'c_{id}', 
        'group': 0, 
        't_progression': participant.progress_time,
        't_death': participant.death_time,
        't_censor': participant.censor_time,
        } for id, participant in enumerate(study.get_control_group())
    ]

    data_all = data_treatment + data_control

    df = pd.DataFrame(data_all)

    df['os_event_time'] = df['t_death']
    df['has_os_event'] = 1

    df['pfs_event_time'] = df['t_censor'].combine_first(df['t_progression']).combine_first(df['t_death'])
    df['has_pfs_event'] = df['t_censor'].apply(lambda x: 0 if pd.notna(x) else 1)

    return df

def get_hr(data, time_col, event_col, group_col):
        cph = CoxPHFitter()
        data_fit = data[[time_col, event_col, group_col]]
        cph.fit(data_fit, duration_col=time_col, event_col=event_col)
        hr = float(cph.hazard_ratios_.iloc[0])  

        return hr

def get_hazard_ratio_pfs(df):

    hr_pfs = get_hr(df, 'pfs_event_time', 'has_pfs_event', 'group')

    return hr_pfs

def get_hazard_ratio_os(df):
    
    hr_os = get_hr(df, 'os_event_time', 'has_os_event', 'group')

    return hr_os

def plot_kaplan_meier(data, time_col, event_col, group_col):

        kmf = KaplanMeierFitter()

        data_treated = data[data[group_col] == 1]
        data_control = data[data[group_col] == 0]

        kmf.fit(data_treated[time_col], data_treated[event_col], label='Treated')
        kmf.plot(ci_show=False)
        kmf.fit(data_control[time_col], data_control[event_col], label='Control')
        kmf.plot(ci_show=False)

def get_plot(df, hr_pfs, hr_os):
    
    figure = plt.figure(figsize=(15, 8))

    plt.subplot(1, 2, 1)
    plt.title(f'Progression-free Survival\n(Hazard Ratio: {round(hr_pfs, 2)})')
    plot_kaplan_meier(df, 'pfs_event_time', 'has_pfs_event', 'group')

    plt.subplot(1, 2, 2)
    plt.title(f'Overall Survival\n(Hazard Ratio: {round(hr_os, 2)})')
    plot_kaplan_meier(df, 'os_event_time', 'has_os_event', 'group')
        
    return figure

def get_plot_pfs(df):
    figure = plt.figure()
    plot_kaplan_meier(df, 'pfs_event_time', 'has_pfs_event', 'group')

    return figure

def get_plot_os(df):
    figure = plt.figure()
    plot_kaplan_meier(df, 'os_event_time', 'has_os_event', 'group')

    return figure