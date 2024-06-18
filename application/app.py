import random
from pathlib import Path
import os

import matplotlib.pyplot as plt
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from faicons import icon_svg
from shiny import render, reactive
from shiny.express import ui, input

###
# General setup and helper functions
###

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

def get_plot_pfs(df):
    figure = plt.figure()
    plot_kaplan_meier(df, 'pfs_event_time', 'has_pfs_event', 'group')

    return figure

def get_plot_os(df):
    figure = plt.figure()
    plot_kaplan_meier(df, 'os_event_time', 'has_os_event', 'group')

    return figure

###
# Shiny application
###

link_mc = "https://i.ibb.co/Bf7XHG4/markov-chain.png"
link_repo = "https://github.com/lulocher/vokinger-os-pfs-simulation"

N = 20000
DEFAULT_P = 0.05

MIN_SLIDER = 0.0
MAX_SLIDER = 0.3

here = Path(__file__).parent

ui.tags.script(
    src="https://mathjax.rstudio.com/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
)
ui.tags.script("if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);")

with ui.div(class_="py-5 text-center mx-0"):
    ui.h3("Clinical Trial Simulator")

ui.accordion()
with ui.accordion(id="acc", open=["Introduction", "Parametrization", "Results"]):  
    with ui.accordion_panel("Introduction"):
        with ui.div(class_="py-4 mx-auto text-left"):
            ui.markdown(
                f"""
                This application simulates the outcome of a clinical trial in oncology using the framework presented in the paper "Why effect sizes are systematically larger for PFS than for OS in clinical trials for cancer drugs" (Locher, Serra-Burriel, Nussli & Vokinger, unpublished manuscript). 
                Parameters for the simulation can be set below. When a parameter is changed, a new trial is automatically simulated. 
                Note that the variance in the results is due to the stochastic nature of the simulation and decreases with larger numbers of participants and longer duration. The outcomes for progression-free survival (PFS) and overall survival (OS) are displayed in the Results tab. 
                The purpose of this application is to allow users to interact with the simulation and observe the impact of different parameters on the outcome of the trial.
                More detailed information can be found in the paper. The underlying code is open-source and available on [GitHub]({link_repo}).
                """
            )

    with ui.accordion_panel("Parametrization"):  

        with ui.layout_columns(col_widths={"sm": 6, "md": (6, 6)}):
            
            with ui.div(class_='mx-auto'):
                @render.image
                def image():
                    img = {'src': os.path.join(here, 'img/markov_chain.png'), 'width': '100%'}
                    return img

            with ui.div():
                with ui.layout_column_wrap(width=1/3, height='15px'):
                    ''
                    'Treatment arm'
                    'Control arm'
                with ui.layout_column_wrap(width=1/3):
                    with ui.tooltip(placement="top"):
                        '$$P_{P|NP}$$'
                        'Probability of transitioning from "no progression" to "progression"'
                    ui.input_slider('p_progression_treatment', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_P, step=0.01)
                    ui.input_slider('p_progression_control', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_P, step=0.01)

                    with ui.tooltip(placement="top"):
                        '$$P_{D|NP}$$'
                        'Probability of transitioning from "no progression" to "dead"'
                    ui.input_slider('p_death_treatment', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_P, step=0.01)
                    ui.input_slider('p_death_control', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_P, step=0.01)

                    with ui.tooltip(placement="top"):
                        '$$P_{D|P}$$'
                        'Probability of transitioning from "progression" to "dead"'
                    ui.input_slider('p_death_given_progression_treatment', None,  MIN_SLIDER, 0.9, DEFAULT_P * 2, step=0.01)
                    ui.input_slider('p_death_given_progression_control', None,  MIN_SLIDER, 0.9, DEFAULT_P * 2, step=0.01)

                    ''
                    ''
                    ui.input_checkbox("show_censoring", "Allow for censoring", False)
                    

                with ui.panel_conditional('input.show_censoring'):
                    with ui.layout_column_wrap(width=1/3):   
                        with ui.tooltip(placement="top"):
                            '$$P_{C|NP}$$'
                            'Probability of transitioning from "no progression" to "censored"'
                        ui.input_slider('p_censor_treatment', None,  MIN_SLIDER, MAX_SLIDER, 0, step=0.025)
                        ui.input_slider('p_censor_control', None,  MIN_SLIDER, MAX_SLIDER, 0, step=0.025)

                        with ui.tooltip(placement="top"):
                            '$$P_{D|C}$$'
                            'Probability of transitioning from "censored" to "dead"'
                        ui.input_slider('p_death_given_censor_treatment', None,  MIN_SLIDER, 0.9, DEFAULT_P, step=0.025)
                        ui.input_slider('p_death_given_censor_control', None,  MIN_SLIDER, 0.9, DEFAULT_P, step=0.025)

        with ui.layout_columns(width=1/4):

            ui.input_slider('n', 'Participants per Arm', 100, 100000, 10000, step=100)
            ui.input_slider('duration', 'Duration of Trial', 5, 50, 20, step=5)

    with ui.accordion_panel("Results"):
        with ui.layout_columns(width=1/3):
            with ui.card():
                ui.h5('Progression-free Survival')
                @render.text
                def hazard_ratio_pfs():
                    return f'Hazard Ratio: {round(get_hazard_ratio_pfs(simulation_results()), 2)}'
                
                @render.plot(height=300)
                def kaplan_meier_plot_pfs():
                    return get_plot_pfs(simulation_results())

            with ui.card():
                ui.h5('Overall Survival')
                @render.text
                def hazard_ratio_os():
                    return f'Hazard Ratio: {round(get_hazard_ratio_os(simulation_results()), 2)}'
                
                @render.plot(height=300)
                def kaplan_meier_plot_os():
                    return get_plot_os(simulation_results())
                
        ui.input_action_button('btn_refresh', 'Simulate new Trial', style='width: 250px; height: 50px; vertical-align: middle', icon=icon_svg('arrow-rotate-right'), class_='btn-primary')


@reactive.Calc
def simulation_results():
    click=input.btn_refresh(),

    return simulate_trial(
        n=input.n(),
        duration=input.duration(),

        p_death_t=input.p_death_treatment(),
        p_death_c=input.p_death_control(), 

        p_death_given_progression_t=input.p_death_given_progression_treatment(),
        p_death_given_progression_c=input.p_death_given_progression_control(),

        p_progression_t=input.p_progression_treatment(),
        p_progression_c=input.p_progression_control(),

        p_censor_t=input.p_censor_treatment() if input.show_censoring() else 0,
        p_censor_c=input.p_censor_control() if input.show_censoring() else 0,

        p_death_given_censor_t=input.p_death_given_censor_treatment() if input.show_censoring() else input.p_death_treatment(),
        p_death_given_censor_c=input.p_death_given_censor_control() if input.show_censoring() else input.p_death_control()
    )




