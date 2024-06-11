#%%
import pandas as pd

from simulation import simulate_trial, get_hazard_ratio_pfs, get_hazard_ratio_os, get_plot

N = 250 * 1000
DURATION = 20

BASE_P_PROGRESSION = 0.1
BASE_P_DEATH = 0.1
BASE_P_CENSOR = 0

settings = {
    'no censoring': {
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
    'non-informative censoring': {    
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH / 2,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.05,
        'p_censor_c': BASE_P_CENSOR + 0.05,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH / 2,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    'informative censoring': {    
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION,
        'p_progression_c': BASE_P_PROGRESSION,
        'p_death_t': BASE_P_DEATH / 2,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR + 0.05,
        'p_censor_c': BASE_P_CENSOR + 0.05,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    },
    'higher progression': {
        'n': N,
        'duration': DURATION,
        'p_progression_t': BASE_P_PROGRESSION * 2,
        'p_progression_c': BASE_P_PROGRESSION * 2,
        'p_death_t': BASE_P_DEATH / 2,
        'p_death_c': BASE_P_DEATH,
        'p_censor_t': BASE_P_CENSOR,
        'p_censor_c': BASE_P_CENSOR,
        'p_death_given_progression_t': BASE_P_DEATH * 1.5,
        'p_death_given_progression_c': BASE_P_DEATH * 1.5,
        'p_death_given_censor_t': BASE_P_DEATH,
        'p_death_given_censor_c': BASE_P_DEATH
    }
}

outcomes = {
    'setting': [],
    'hr_pfs': [],
    'hr_os': []
}

for setting in settings.keys():
    df_trial = simulate_trial(**settings[setting])

    hazard_ratio_pfs = get_hazard_ratio_pfs(df_trial)
    hazard_ratio_os = get_hazard_ratio_os(df_trial)

    outcomes['setting'].append(setting)
    outcomes['hr_pfs'].append(hazard_ratio_pfs)
    outcomes['hr_os'].append(hazard_ratio_os)

df_outcomes = pd.DataFrame(outcomes)

