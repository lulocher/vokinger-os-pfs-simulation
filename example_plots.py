import matplotlib.pyplot as plt
import os
import pandas as pd

from simulation import simulate_trial, get_hazard_ratio_pfs, get_hazard_ratio_os, get_plot

path = os.path.dirname(__file__)

N = 200000

BASE_P_PROGRESSION = 0.15
BASE_P_DEATH = 0.15
BASE_P_CENSOR = 0

                                                                       
settings = {
    '1_progression_driven_low_translation': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION / 2,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.1,
        'h_death_given_progression_c': BASE_P_DEATH + 0.1,
        'h_death_given_censor_t': BASE_P_DEATH,
        'h_death_given_censor_c': BASE_P_DEATH
    },
   
    '2_progression_driven_high_translation': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION / 2,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.6,
        'h_death_given_progression_c': BASE_P_DEATH + 0.6,
        'h_death_given_censor_t': BASE_P_DEATH,
        'h_death_given_censor_c': BASE_P_DEATH
    },

    '3_progression_driven_differential_translation': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION / 2,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.6,
        'h_death_given_progression_c': BASE_P_DEATH + 0.1,
        'h_death_given_censor_t': BASE_P_DEATH,
        'h_death_given_censor_c': BASE_P_DEATH
    },

    '4_censoring_driven_negative_small_difference': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION  - 0.05,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH  - 0.05,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR + 0.1,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.05,
        'h_death_given_progression_c': BASE_P_DEATH + 0.05,
        'h_death_given_censor_t': BASE_P_DEATH * (4/3),
        'h_death_given_censor_c': BASE_P_DEATH
    },

    '5_censoring_driven_negative_large_difference': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION - 0.05,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH  - 0.05,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR + 0.1,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.05,
        'h_death_given_progression_c': BASE_P_DEATH + 0.05,
        'h_death_given_censor_t': BASE_P_DEATH * 2,
        'h_death_given_censor_c': BASE_P_DEATH
    },

    '6_censoring_driven_positive_large_difference': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION,
        'h_progression_c': BASE_P_PROGRESSION + 0.05,
        'h_death_t': BASE_P_DEATH,
        'h_death_c': BASE_P_DEATH + 0.05,
        'h_censor_t': BASE_P_CENSOR,
        'h_censor_c': BASE_P_CENSOR + 0.1,
        'h_death_given_progression_t': BASE_P_DEATH + 0.05,
        'h_death_given_progression_c': BASE_P_DEATH + 0.05,
        'h_death_given_censor_t': BASE_P_DEATH,
        'h_death_given_censor_c': BASE_P_DEATH / 2,
    },

    '7_combined': {
        'n': N,
        'h_progression_t': BASE_P_PROGRESSION / 2,
        'h_progression_c': BASE_P_PROGRESSION,
        'h_death_t': BASE_P_DEATH - 0.05,
        'h_death_c': BASE_P_DEATH,
        'h_censor_t': BASE_P_CENSOR + 0.1,
        'h_censor_c': BASE_P_CENSOR,
        'h_death_given_progression_t': BASE_P_DEATH + 0.6,
        'h_death_given_progression_c': BASE_P_DEATH + 0.05,
        'h_death_given_censor_t': BASE_P_DEATH * 2,
        'h_death_given_censor_c': BASE_P_DEATH
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