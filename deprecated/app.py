from shiny import App, render, ui, reactive
from faicons import icon_svg
from shiny.types import ImgData
from simulation import simulate_trial, get_plot, get_plot_pfs, get_plot_os, get_plot_eos, get_hazard_ratio_pfs, get_hazard_ratio_os, get_hazard_ratio_eos
import os

DIR = os.path.dirname(__file__)

N = 20000
DEFAULT_H = 0.1

MIN_SLIDER = 0.0
MAX_SLIDER = 0.3

app_ui = ui.page_sidebar( 

    ui.sidebar(
        {'style': 'padding-top:30; padding-bottom:30; padding-right:20; padding-left:20;'},
        ui.markdown(
            '''
            This visualization allows you to visualize trial outcomes for different hazards.

            *You can set the parameters below to explore different settings*

            '''
        ),

        ui.output_image('markov_chain', height='250px'),

        ui.div(
            {'style': 'font-size:12px; font-weight: normal;width: 100%'},
            ui.accordion(
                ui.accordion_panel(
                    ui.output_image('prob_progression_symbol', height='20px'),
                    ui.row(
                        ui.column(6, ui.input_slider('p_progression_treatment', 'Treatment', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)),
                        ui.column(6, ui.input_slider('p_progression_control', 'Control', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025))
                    ),
                    value='prob_progression'
                ),
                ui.accordion_panel(
                    ui.output_image('prob_censor_symbol', height='20px'),
                    ui.row(
                        ui.column(6, ui.input_slider('p_censor_treatment', 'Treatment', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)),
                        ui.column(6, ui.input_slider('p_censor_control', 'Control', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025))
                    ),
                    value='prob_censor'
                ),
                ui.accordion_panel(
                    ui.output_image('prob_death_no_progression_symbol', height='20px'),
                    ui.row(
                        ui.column(6, ui.input_slider('p_death_treatment', 'Treatment', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025)),
                        ui.column(6, ui.input_slider('p_death_control', 'Control', MIN_SLIDER, MAX_SLIDER, DEFAULT_H, step=0.025))
                    ),
                    value='prob_death_no_progression'
                ),
                ui.accordion_panel(
                    ui.output_image('prob_death_censor_symbol', height='20px'),
                    ui.row(
                        ui.column(6, ui.input_slider('p_death_given_censor_treatment', 'Treatment', MIN_SLIDER, 1, DEFAULT_H, step=0.025)),
                        ui.column(6, ui.input_slider('p_death_given_censor_control', 'Control', MIN_SLIDER, 1, DEFAULT_H, step=0.025))
                    ),
                    value='prob_death_censor'
                ),
                ui.accordion_panel( 
                    ui.output_image('prob_death_progression_symbol', height='20px'),
                    ui.row(
                        ui.column(6, ui.input_slider('p_death_given_progression_treatment', 'Treatment', MIN_SLIDER, 1, DEFAULT_H + 0.1, step=0.025)),
                        ui.column(6, ui.input_slider('p_death_given_progression_control', 'Control', MIN_SLIDER, 1, DEFAULT_H + 0.1, step=0.025))
                    ),
                    value='prob_death_progression'
                ),
                open=False
            )
        ),
        width='500px'
    ),

    ui.div(
        ui.div(
            ui.row(
                ui.input_slider('n', 'Participants per Arm', 100, 100000, 10000, step=100, width='200px'),
                ui.input_slider('duration', 'Duration of Trial', 10, 50, 20, step=5, width='200px'),
                ui.input_action_button('btn_refresh', 'Simulate new Trial', style='width: 200px; height: 75px; vertical-align: middle', icon=icon_svg('arrow-rotate-right'), class_='btn-primary'),
                style='padding-top: 10px; padding-bottom: 10px;'
            ),
            ui.row(
                ui.column(4, ui.h4('Progression-free Survival')),
                ui.column(4, ui.h4('Overall Survival')),
                ui.column(4, ui.h4('Expected Overall Survival')),
            ),
            ui.row(
                ui.column(
                    4,
                    ui.value_box(
                        'Hazard Ratio',
                        ui.output_text('hazard_ratio_pfs'),
                        showcase_layout='bottom',
                        theme='text-black',
                    ),
                    ui.card(
                        ui.output_plot('kaplan_meier_plot_pfs'),
                        style='border-radius: 10px;'
                    )
                    
                ),
                ui.column(
                    4,
                    ui.value_box(
                        'Hazard Ratio',
                        ui.output_text('hazard_ratio_os'),
                        showcase_layout='bottom',
                        theme='text-black',
                    ),
                    ui.card(
                        ui.output_plot('kaplan_meier_plot_os'),
                        style='border-radius: 10px;'
                    )
                ),
                ui.column(
                    4, 
                    ui.value_box(
                        'Hazard Ratio',
                        ui.output_text('hazard_ratio_eos'),
                        showcase_layout='bottom',
                        theme='text-black',
                    ),
                    ui.card(
                        ui.output_plot('kaplan_meier_plot_eos'),
                        style='border-radius: 10px;'
                    )
                )
            ) 
        ),
    ),
    
    title='Trial Outcome Calculator'
)

def server(input, output, session):

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

    @render.text
    def hazard_ratio_os():
        return round(get_hazard_ratio_os(simulation_results()), 2)

    @render.text
    def hazard_ratio_pfs():
        return round(get_hazard_ratio_pfs(simulation_results()), 2)
    
    @render.text
    def hazard_ratio_eos():
        return round(get_hazard_ratio_eos(simulation_results()), 2)

    @render.plot
    def kaplan_meier_plot():
        return get_plot(simulation_results())

    @render.plot
    def kaplan_meier_plot_pfs():
        return get_plot_pfs(simulation_results())

    @render.plot
    def kaplan_meier_plot_os():
        return get_plot_os(simulation_results())

    @render.plot
    def kaplan_meier_plot_eos():
        return get_plot_eos(simulation_results())

    @render.image
    def markov_chain():
        img: ImgData = {'src':  os.path.join(DIR, 'img/markov_chain.png'), 'width': '90%'}
        return img

    @render.image
    def prob_progression_symbol():
        img: ImgData = {'src':  os.path.join(DIR, 'img/p_p_np_symbol.png'), 'height': '20px'}
        return img

    @render.image
    def prob_censor_symbol():
        img: ImgData = {'src':  os.path.join(DIR, 'img/p_c_np_symbol.png'), 'height': '20px'}
        return img

    @render.image
    def prob_death_no_progression_symbol():
        img: ImgData = {'src':  os.path.join(DIR, 'img/p_d_np_symbol.png'), 'height': '20px'}
        return img

    @render.image
    def prob_death_progression_symbol():
        img: ImgData = {'src':  os.path.join(DIR, 'img/p_d_p_symbol.png'), 'height': '20px'}
        return img

    @render.image
    def prob_death_censor_symbol():
        img: ImgData = {'src':  os.path.join(DIR, 'img/p_d_c_symbol.png'), 'height': '20px'}
        return img



app = App(app_ui, server)
