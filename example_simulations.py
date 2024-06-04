import matplotlib.pyplot as plt
import os
import pandas as pd

from app import simulate_trial, get_hazard_ratio_pfs, get_hazard_ratio_os, get_plot

path = os.path.dirname(__file__)

N = 200000
DURATION = 1000

BASE_P_PROGRESSION = 0.15
BASE_P_DEATH = 0.15
BASE_P_CENSOR = 0

                                                                       
settings = {
    '1_progression_driven_low_translation': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION / 2,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR,
        'p_censor_c': BASE_P_CENSOR,
        'p_death_given_progression_t': BASE_P_DEATH + 0.1,
        'p_death_given_progression_c': BASE_P_DEATH + 0.1,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
   
    '2_progression_driven_high_translation': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION / 2,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR,
        'p_censor_c': BASE_P_CENSOR,
        'p_death_given_progression_t': BASE_P_DEATH + 0.6,
        'p_death_given_progression_c': BASE_P_DEATH + 0.6,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '3_post_progression_death_driven': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR,
        'p_censor_c': BASE_P_CENSOR,
        'p_death_given_progression_t': BASE_P_DEATH + 0.05,
        'p_death_given_progression_c': BASE_P_DEATH + 0.2,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '4_pre_progression_death_driven': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH / 2,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR,
        'p_censor_c': BASE_P_CENSOR,
        'p_death_given_progression_t': BASE_P_DEATH + 0.1,
        'p_death_given_progression_c': BASE_P_DEATH + 0.1,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '5_censoring_driven_treat_low': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION /2,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH / 2,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.1,
        'p_censor_c': BASE_P_CENSOR + 0.05,
        'p_death_given_progression_t': BASE_P_DEATH + 0.1,
        'p_death_given_progression_c': BASE_P_DEATH + 0.1,
        'p_death_given_censor_t': BASE_P_DEATH + 0.05,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '6_censoring_driven_treat_high': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * (3/4),
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH * (3/4),
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.1,
        'p_censor_c': BASE_P_CENSOR + 0.05,
        'p_death_given_progression_t': BASE_P_DEATH + 0.2,
        'p_death_given_progression_c': BASE_P_DEATH + 0.2,
        'p_death_given_censor_t': BASE_P_DEATH + 0.3,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '7_censoring_driven_control_high': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * (3/4),
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH * (3/4),
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.05,
        'p_censor_c': BASE_P_CENSOR + 0.1,
        'p_death_given_progression_t': BASE_P_DEATH + 0.2,
        'p_death_given_progression_c': BASE_P_DEATH + 0.2,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH + 0.3
    }
}

plots = []

for setting in settings:
    print(f'Processing setting {setting}...')

    df_trial = simulate_trial(**settings[setting])

    hazard_ratio_pfs = get_hazard_ratio_pfs(df_trial)
    hazard_ratio_os = get_hazard_ratio_os(df_trial)

    plot = get_plot(df_trial, hazard_ratio_pfs, hazard_ratio_os)

    plots.append((setting, plot))

for setting, plot in plots:
    plot.savefig(f'{path}/plots/plot_{setting}.png')

print('Saved all plots...')

df_settings = pd.DataFrame.from_dict(settings, orient='index')
df_settings.to_csv(f'{path}/plots/settings.csv')

print('Saved settings...')