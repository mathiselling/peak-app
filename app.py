import pandas as pd
from shiny import render
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
import plotly.express as px
import faicons as fa
from ipyleaflet import Map, Marker, basemaps

df01 = pd.read_csv('peaks2.csv').rename(columns={'Metres': 'Meters'})
# Pre-process the DataFrame to ensure 'latlng' column contains tuples
df01['latlng'] = df01['latlng'].apply(lambda x: tuple(map(float, x.strip('[]').split(', '))) if isinstance(x, str) else x)

# Title
ui.page_opts(title='MyPeaks', fillable=True)

# Icons
github_icon = fa.icon_svg('github', width='24px', height='24px', fill='black')
mountain_icon = fa.icon_svg('mountain')

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

# Main content
with ui.nav_panel('Map'):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            'Peaks'
            @render.text
            def peak_names_map():
                if input.radio.get() == 'Specify':
                    return ', '.join(input.selectize())
                elif input.radio.get() == 'Top-list':
                    return 'Top-List'
                else:
                    return None
                
    @render_widget
    def map():
        m = Map(basemap=basemaps.Esri.NatGeoWorldMap, zoom=2, center=(27.986065, 86.922623), scroll_wheel_zoom=True)

        if input.radio.get() == 'Specify':
            for mountain in input.selectize():
                latlng = df01.loc[df01['Mountain'] == mountain, 'latlng'].iloc[0]
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add_layer(marker)
        elif input.radio.get() == 'Top-list':
            for mountain in df01['Mountain'].iloc[(input.begin_list() - 1):input.end_list()]:
                latlng = df01.loc[df01['Mountain'] == mountain, 'latlng'].iloc[0]
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add(marker)
            
        return m
    
with ui.nav_panel('Plot'):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            'Peaks'
            @render.text
            def peak_names_plot():
                if input.radio.get() == 'Specify':
                    return ', '.join(input.selectize())
                elif input.radio.get() == 'Top-list':
                    return 'Top-List'
                else:
                    return None

    @render_plotly
    def plot():
        if input.radio.get() == 'Specify':
            df02 = df01[df01['Mountain'].isin(input.selectize())]
        elif input.radio.get() == 'Top-list':
            df02 = df01.iloc[(input.begin_list() - 1):input.end_list()]
        else:
            df02 = pd.DataFrame(columns=df01.columns)
        
        scatter = px.scatter(df02, x='Mountain', y='Meters', hover_data=['Feet', 'Note'])
        scatter.update_traces(marker=dict(size=30), marker_symbol='triangle-up')
        scatter.update_layout(xaxis_title='', font=dict(size=18), modebar_remove=['resetScale', 'lasso2d', 'select2d'])
        return scatter

with ui.nav_panel('Stats'):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            'Peaks'
            @render.text
            def peak_names_stats():
                if input.radio.get() == 'Specify':
                    return ', '.join(input.selectize())
                elif input.radio.get() == 'Top-list':
                    return 'Top-List'
                else:
                    return None

with ui.nav_control():
    ui.a(
        github_icon,
        href='https://github.com/mathiselling/peak-app',
        target='_blank',
    )