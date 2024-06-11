import os
import pandas as pd
from string import ascii_letters


from simulation import simulate_trial, get_hazard_ratio_pfs, get_hazard_ratio_os, get_plot

path = os.path.dirname(__file__)

N = 250 * 1000
DURATION = 20

BASE_P_PROGRESSION = 0.025
BASE_P_DEATH = 0.025
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
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
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
        'p_death_given_progression_t': BASE_P_DEATH * 4,
        'p_death_given_progression_c': BASE_P_DEATH * 4,
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
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 4,
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
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '5_censoring_driven_treat_low': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * (3/4),
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH * (3/4),
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.05,
        'p_censor_c': BASE_P_CENSOR + 0.025,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH * 1.5,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '6_censoring_driven_treat_high': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * (3/4),
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH * (3/4),
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.05,
        'p_censor_c': BASE_P_CENSOR + 0.025,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH * 3,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    '7_censoring_driven_control_high': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * (3/4),
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH * (3/4),
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.025,
        'p_censor_c': BASE_P_CENSOR + 0.05,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH * 3
    }
}

plots = []

def generate_table_row(index, params):
    letter = ascii_letters[index]
    row = f"{letter})"
    for key in params:
        if key != 'duration' and key != 'n':
            row += f" & {round(params[key], 3)}"
        
    return row + "\\\\\n\\hline\n"

table_out = ''

for i, (setting, params) in enumerate(settings.items()):
    print(f'Processing setting {setting}...')

    table_out += generate_table_row(i, params)
    df_trial = simulate_trial(**params)

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

print(f'Printing settings table for LaTex:\n{table_out}')
