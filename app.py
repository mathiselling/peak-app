import pandas as pd
from shiny import render
from shiny.express import ui, input
from shinywidgets import render_plotly
import plotly.express as px
import faicons as fa

df01 = pd.read_csv('peaks.csv').rename(columns={'Metres': 'Meters'})
df01['Note'] = df01['Range'].str.strip().str.cat(df01['Location'].str.strip(), sep=' ', na_rep='')

# Title
ui.page_opts(title='MyPeaks', fillable=True)

# Sidebar
with ui.sidebar(open='open'):
    ui.input_radio_buttons(
        'radio',
        'Do you prefer to select mountains from a list, write down their names, or specify a range in the top-list?',
        ['Select', 'Write down', 'Top-list']
    )
    with ui.panel_conditional('input.radio === "Write down"'):
        ui.input_text('peak_1', 'Mountain 1')
        ui.input_text('peak_2', 'Mountain 2')
        ui.input_text('peak_3', 'Mountain 3')
        ui.input_text('peak_4', 'Mountain 4')
        ui.input_text('peak_5', 'Mountain 5')
    with ui.panel_conditional('input.radio === "Select"'):
        mountain_options = df01['Mountain'].unique().tolist()
        ui.input_selectize(
            'selectize',  
            'Select mountains below:',  
            {option: option for option in mountain_options},  
            multiple=True,
        )
    with ui.panel_conditional('input.radio === "Top-list"'):
        ui.input_numeric('begin_list', 'Start of the list', 1, min=1, max=1645)
        ui.input_numeric('end_list', 'End of the list', 14, min=1, max=1645)

# Main content
ICONS = {
    'mountain': fa.icon_svg('mountain')
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS['mountain']):
        'Peaks'
        @render.text
        def peak_names():
            if input.radio.get() == 'Write down':
                peak_list = [input.peak_1(), input.peak_2(), input.peak_3(), input.peak_4(), input.peak_5(),]
                filtered_peak_list = [peak for peak in peak_list if peak]
                return ', '.join(filtered_peak_list)
            elif input.radio.get() == 'Select':
                selected_peaks = input.selectize()
                return ', '.join(selected_peaks)
            elif input.radio.get() == 'Top-list':
                return 'Top-List'
            else:
                return None

@render_plotly
def plot():
    if input.radio.get() == 'Write down':
        peak_1_value = input.peak_1()
        peak_2_value = input.peak_2()
        peak_3_value = input.peak_3()
        peak_4_value = input.peak_4()
        peak_5_value = input.peak_5()
        df02 = df01.query(f'Mountain in ["{peak_1_value}", "{peak_2_value}", "{peak_3_value}", "{peak_4_value}", "{peak_5_value}",]')
    elif input.radio.get() == 'Select':
        selected_peaks = input.selectize()
        df02 = df01[df01['Mountain'].isin(selected_peaks)]
    elif input.radio.get() == 'Top-list':
        df02 = df01.iloc[(input.begin_list() - 1):input.end_list()]
    else:
        df02 = pd.DataFrame(columns=df01.columns)
    
    scatter = px.scatter(df02, x='Mountain', y='Meters', hover_data=['Feet', 'Note'])
    scatter.update_traces(marker=dict(size=60), marker_symbol='triangle-up')
    scatter.update_layout(xaxis_title='', font=dict(size=18))
    return scatter
