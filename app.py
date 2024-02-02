from functools import partial
from pathlib import Path
from faicons import icon_svg

from shiny.ui import output_image
from shiny import render, reactive
from shiny.express import ui, input, render
from shiny.types import ImgData

from simulation import simulate_trial, get_plot_pfs, get_plot_os, get_plot_eos, get_hazard_ratio_pfs, get_hazard_ratio_os, get_hazard_ratio_eos

link_mc = "https://i.ibb.co/Bf7XHG4/markov-chain.png"

N = 20000
DEFAULT_H = 0.1

MIN_SLIDER = 0.0
MAX_SLIDER = 0.3

here = Path(__file__).parent

ui.tags.script(
    src="https://mathjax.rstudio.com/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
)
ui.tags.script("if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);")

with ui.div(class_="py-5 text-center mx-0"):
    ui.h3("Clinical Trial Outcome Simulator")

ui.accordion()
with ui.accordion(id="acc", open=["Introduction", "Parametrization", "Results"]):  
    with ui.accordion_panel("Introduction"):
        with ui.div(class_="py-4 mx-auto text-left"):
            ui.markdown(
                """
                This app simulates the outcome of a clinical trial in oncology using the framework of ... Parameters can be set below. When a parameter is changed, 
                a new trial is automatically simulated. Note that the variance in the results is due to the stochastic nature of the simulation and increases 
                with a smaller number of participants and a shorter duration of the trial. The results for Progression-free Survival (PFS), Expected Overall Survival (EOS), 
                and Overall Survival (OS) are displayed in the Results tab. The goal of this application is to demonstrate the impact of different parametrizations on the
                endpoints. For more detailed information, please refer to ... . The code is open-source and available on GitHub.
                """
            )

    with ui.accordion_panel("Parametrization"):  

        with ui.layout_columns(col_widths={"sm": 6, "md": (6, 6)}):
            
            with ui.div(class_='mx-auto my-auto'):
                ui.tags.img(src=link_mc, width="100%")

            with ui.div():
                with ui.layout_column_wrap(width=1/3, height='15px'):
                    ''
                    'Treatment Arm'
                    'Control Arm'
                with ui.layout_column_wrap(width=1/3):
                    '$$P_{P|NP}$$'
                    ui.input_slider('p_progression_treatment', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    ui.input_slider('p_progression_control', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    '$$P_{C|NP}$$'
                    ui.input_slider('p_censor_treatment', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    ui.input_slider('p_censor_control', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    '$$P_{D|NP}$$'
                    ui.input_slider('p_death_treatment', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    ui.input_slider('p_death_control', None,  MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)
                    '$$P_{D|P}$$'
                    ui.input_slider('p_death_given_progression_treatment', None,  MIN_SLIDER, 0.9, DEFAULT_H + 0.1, step=0.025)
                    ui.input_slider('p_death_given_progression_control', None,  MIN_SLIDER, 0.9, DEFAULT_H + 0.1, step=0.025)
                    '$$P_{D|C}$$'
                    ui.input_slider('p_death_given_censor_treatment', None,  MIN_SLIDER, 0.9, DEFAULT_H, step=0.025)
                    ui.input_slider('p_death_given_censor_control', None,  MIN_SLIDER, 0.9, DEFAULT_H, step=0.025)

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
                ui.h5('Expected Overall Survival')
                @render.text
                def hazard_ratio_eos():
                    return f'Hazard Ratio: {round(get_hazard_ratio_eos(simulation_results()), 2)}'
                
                @render.plot(height=300)
                def kaplan_meier_plot_eos():
                    return get_plot_eos(simulation_results())

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

        p_death_given_censor_t=input.p_death_given_censor_treatment(),
        p_death_given_censor_c=input.p_death_given_censor_control(),

        p_progression_t=input.p_progression_treatment(),
        p_progression_c=input.p_progression_control(),

        p_censor_t=input.p_censor_treatment(),
        p_censor_c=input.p_censor_control(),
    )




