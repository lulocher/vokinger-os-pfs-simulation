import random
import matplotlib.pyplot as plt
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter

NO_PROGRESSION = 'no progression'
PROGRESSED = 'progressed'
CENSORED = 'censored'
DEAD = 'dead'


class StudyParticipant:
    """
    Class representing a participant in a clinical trial
    """
    def __init__(self):
        self.progress_time = None
        self.death_time = None
        self.censor_time = None
        self.state = NO_PROGRESSION
    
    def update_state(self, state, t):
        self.state = state
        if state == PROGRESSED:
            self.progress(t)
        elif state == CENSORED:
            self.censor(t)
        elif state == DEAD:
            self.die(t)

    def progress(self, t):
        self.progress_time = t

    def die(self, t):
        self.death_time = t

    def censor(self, t):
        self.censor_time = t


class Study:
    """
    Class representing a clinical trial
    """

    def __init__(
            self, n, duration,
            p_progression_treatment, p_death_treatment, p_censor_treatment,  p_death_given_progression_treatment, p_death_given_censor_treatment,
            p_progression_control, p_death_control, p_censor_control, p_death_given_progression_control, p_death_given_censor_control
            ):
        self.t = 0
        self.duration = duration
        self.p_progression_t = p_progression_treatment
        self.p_death_t = p_death_treatment
        self.p_censor_t = p_censor_treatment
        self.p_death_given_progression_t = p_death_given_progression_treatment
        self.p_death_given_censor_t = p_death_given_censor_treatment
        self.p_progression_c = p_progression_control
        self.p_death_c = p_death_control
        self.p_censor_c = p_censor_control
        self.p_death_given_progression_c = p_death_given_progression_control
        self.p_death_given_censor_c = p_death_given_censor_control

        self.treatment_group = [StudyParticipant() for x in range(n)]
        self.control_group = [StudyParticipant() for x in range(n)]
        self.complete = False

    def get_treatment_group(self):
        return self.treatment_group
    
    def get_control_group(self):
        return self.control_group
    
    def check_complete(self):
        if self.t >= self.duration:
            return True

        for participant in self.treatment_group + self.control_group:
            if not participant.death_time:
                return False

        return True

    def simulate_period(self):
        self.t += 1

        def draw_events(t, participant, p_p, p_d, p_c, p_d_g_p, p_d_g_c):

            if participant.death_time:
                return
            
            if participant.censor_time: 
                state = random.choices([DEAD, CENSORED], weights = [p_d_g_c, 1-p_d_g_c], k=1)[0]

            elif participant.progress_time:
                state = random.choices([DEAD, PROGRESSED], weights = [p_d_g_p, 1-p_d_g_p], k=1)[0]

            else:
                state = random.choices([DEAD, PROGRESSED, CENSORED, NO_PROGRESSION], weights = [p_d, p_p, p_c, 1-p_d-p_p-p_c], k=1)[0]

            if state != participant.state:
                participant.update_state(state, t)
            
        for participant in self.treatment_group:
            draw_events(self.t, participant, self.p_progression_t, self.p_death_t, self.p_censor_t, self.p_death_given_progression_t, self.p_death_given_censor_t)
        
        for participant in self.control_group:
            draw_events(self.t, participant, self.p_progression_c, self.p_death_c, self.p_censor_c, self.p_death_given_progression_c, self.p_death_given_censor_c)

        self.complete = self.check_complete()



def simulate_trial(n, duration, p_progression_t, p_death_t, p_censor_t, p_death_given_progression_t, p_death_given_censor_t, p_progression_c, p_death_c, p_censor_c, p_death_given_progression_c, p_death_given_censor_c):
    study = Study(
        n=n,
        duration=duration,
        p_progression_treatment=p_progression_t,
        p_death_treatment=p_death_t,
        p_censor_treatment=p_censor_t,
        p_death_given_progression_treatment=p_death_given_progression_t,
        p_death_given_censor_treatment=p_death_given_censor_t,
        p_progression_control=p_progression_c,
        p_death_control=p_death_c,
        p_censor_control=p_censor_c,
        p_death_given_progression_control=p_death_given_progression_c,
        p_death_given_censor_control = p_death_given_censor_c
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

    df['duration'] = duration

    df['pfs_event_time'] = df['t_censor'].combine_first(df['t_progression']).combine_first(df['t_death']).combine_first(df['duration'])
    df['has_pfs_event'] = df.apply(lambda x: 0 if pd.notna(x['t_censor']) or (pd.isna(x['t_censor']) and pd.isna(x['t_progression']) and pd.isna(x['t_death'])) else 1, axis=1)

    df['os_event_time'] = df['t_death'].combine_first(df['duration'])
    df['has_os_event'] = df['t_death'].apply(lambda x: 1 if pd.notna(x) else 0)

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
    figure = plt.figure(figsize=(8, 4))

    plt.subplot(1, 2, 1)
    plt.title(f'PFS\n(HR: {round(hr_pfs, 2)})')
    plot_kaplan_meier(df, 'pfs_event_time', 'has_pfs_event', 'group')

    plt.subplot(1, 2, 2)
    plt.title(f'OS\n(HR: {round(hr_os, 2)})')
    plot_kaplan_meier(df, 'os_event_time', 'has_os_event', 'group')
        
    return figure