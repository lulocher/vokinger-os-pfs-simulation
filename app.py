from shiny import App, render, ui, reactive
from shiny.types import ImgData
from simulation import simulate_trial, get_plot, get_plot_pfs, get_plot_os, get_hazard_ratio_pfs, get_hazard_ratio_os
import os

DIR = os.path.dirname(__file__)

N = 10000
DEFAULT_H = 0.2

app_ui = ui.page_sidebar( 

    ui.sidebar(
        {"style": 'padding-top:30; padding-bottom:30; padding-right:20; padding-left:20'},
        ui.markdown(
            """
            This visualization allows you to Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor.

            *You can set the parameters here to explore different settings.* **Add more description**.

            """
        ),

        ui.output_image("formula", height='50px', ),

        ui.div(
            {"style": "font-size:12px; font-weight: normal;"},
            ui.accordion(
                ui.accordion_panel(
                    "Hazard Progression",
                    ui.row(
                        ui.column(6, ui.input_slider("h_progression_treatment", 'Treatment', 0.001, 1, DEFAULT_H, step=0.05)),
                        ui.column(6, ui.input_slider("h_progression_control", 'Control', 0.001, 1, DEFAULT_H, step=0.05))
                    )
                
                ),
                ui.accordion_panel(
                    "Hazard Unknown",
                    ui.row(
                        ui.column(6, ui.input_slider("h_censor_treatment", 'Treatment', 0.001, 1, DEFAULT_H, step=0.05)),
                        ui.column(6, ui.input_slider("h_censor_control", 'Control', 0.001, 1, DEFAULT_H, step=0.05))
                    )
                ),
                ui.accordion_panel(
                    "Hazard Death (No progression)",
                    ui.row(
                        ui.column(6, ui.input_slider("h_death_treatment", 'Treatment', 0.001, 1, DEFAULT_H, step=0.05)),
                        ui.column(6, ui.input_slider("h_death_control", 'Control', 0.001, 1, DEFAULT_H, step=0.05))
                    )
                ),
                ui.accordion_panel(
                    "Hazard Death (Progression unknown)",
                    ui.row(
                        ui.column(6, ui.input_slider("h_death_given_censor_treatment", 'Treatment', 0.001, 1, DEFAULT_H + 0.1, step=0.05)),
                        ui.column(6, ui.input_slider("h_death_given_censor_control", 'Control', 0.001, 1, DEFAULT_H + 0.1, step=0.05))
                    )
                ),
                ui.accordion_panel(
                    "Hazard Death (Progression)",
                    ui.row(
                        ui.column(6, ui.input_slider("h_death_given_progression_treatment", 'Treatment', 0.001, 1, DEFAULT_H + 0.1, step=0.05)),
                        ui.column(6, ui.input_slider("h_death_given_progression_control", 'Control', 0.001, 1, DEFAULT_H + 0.1, step=0.05))
                    )
                ),
                open=False
            )   
        ),
        width="400px"
    ),

    ui.div(
        ui.div(
            ui.row(
                ui.column(
                    6,
                    ui.h4('Progression-free Survival'),
                    ui.value_box(
                        "Hazard Ratio",
                        ui.output_text("hazard_ratio_pfs"),
                        showcase_layout='bottom',
                        theme="text-black",
                    ),
                    ui.card(
                        ui.output_plot('kaplan_meier_plot_pfs'),
                        style='border-radius: 10px;'
                    )
                    
                ),
                ui.column(
                    6, 
                    ui.h4('Overall Survival'),
                    ui.value_box(
                        "Hazard Ratio",
                        ui.output_text("hazard_ratio_os"),
                        showcase_layout='bottom',
                        theme="text-black",
                    ),
                    ui.card(
                        ui.output_plot('kaplan_meier_plot_os'),
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
        # TODO: Add simulation here
        return simulate_trial(
            n=N,

            h_death_t=input.h_death_treatment(),
            h_death_c=input.h_death_control(), 

            h_death_given_progression_t=input.h_death_given_progression_treatment(),
            h_death_given_progression_c=input.h_death_given_progression_control(),

            h_death_given_censor_t=input.h_death_given_censor_treatment(),
            h_death_given_censor_c=input.h_death_given_censor_control(),

            h_progression_t=input.h_progression_treatment(),
            h_progression_c=input.h_progression_control(),

            h_censor_t=input.h_censor_treatment(),
            h_censor_c=input.h_censor_control(),
        )

    @render.text
    def hazard_ratio_os():
        return round(get_hazard_ratio_os(simulation_results()), 2)

    @render.text
    def hazard_ratio_pfs():
        return round(get_hazard_ratio_pfs(simulation_results()), 2)

    @render.plot
    def kaplan_meier_plot():
        return get_plot(simulation_results())

    @render.plot
    def kaplan_meier_plot_pfs():
        return get_plot_pfs(simulation_results())

    @render.plot
    def kaplan_meier_plot_os():
        return get_plot_os(simulation_results())

    @render.image
    def formula():
        img: ImgData = {"src":  os.path.join(DIR, "img/math_ex.png"), "width": "90%"}
        return img



app = App(app_ui, server)
