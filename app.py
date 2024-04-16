import pandas as pd
from shiny import render
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
import plotly.express as px
import faicons as fa
import ipyleaflet as L

df01 = pd.read_csv('peaks.csv').rename(columns={'Metres': 'Meters'})
df01['Note'] = df01['Range'].str.strip().str.cat(df01['Location'].str.strip(), sep=' ', na_rep='')

# Title
ui.page_opts(title='MyPeaks', fillable=True)

# Push nav_panel to the right
ui.nav_spacer()

# Sidebar
with ui.sidebar(open='open'):
    ui.input_radio_buttons(
        'radio',
        'Do you want to specify the mountains yourself or explore the top-list?',
        ['Specify', 'Top-list']
    )
    with ui.panel_conditional('input.radio === "Specify"'):
        mountain_options = df01['Mountain'].unique().tolist()
        ui.input_selectize(
            'selectize',  
            'Select mountains below or start writing:',  
            {option: option for option in mountain_options},  
            multiple=True,
        )
    with ui.panel_conditional('input.radio === "Top-list"'):
        ui.input_numeric('begin_list', 'Start of the list', 1, min=1, max=1645)
        ui.input_numeric('end_list', 'End of the list', 14, min=1, max=1645)
    ui.input_dark_mode(mode="light")

# Main content
ICONS = {
    'mountain': fa.icon_svg('mountain')
}

with ui.nav_panel("Plot"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=ICONS['mountain']):
            'Peaks'
            @render.text
            def peak_names():
                if input.radio.get() == 'Specify':
                    selected_peaks = input.selectize()
                    return ', '.join(selected_peaks)
                elif input.radio.get() == 'Top-list':
                    return 'Top-List'
                else:
                    return None

    @render_plotly
    def plot():
        if input.radio.get() == 'Specify':
            selected_peaks = input.selectize()
            df02 = df01[df01['Mountain'].isin(selected_peaks)]
        elif input.radio.get() == 'Top-list':
            df02 = df01.iloc[(input.begin_list() - 1):input.end_list()]
        else:
            df02 = pd.DataFrame(columns=df01.columns)
        
        scatter = px.scatter(df02, x='Mountain', y='Meters', hover_data=['Feet', 'Note'])
        scatter.update_traces(marker=dict(size=60), marker_symbol='triangle-up')
        scatter.update_layout(xaxis_title='', font=dict(size=18), modebar_remove=['resetScale', 'lasso2d', 'select2d'])
        return scatter

with ui.nav_panel("Map"):
    @render_widget
    def map():
        return L.Map(zoom=15, center=(50.948529, 6.918097))