import pandas as pd
from shiny import render
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
import plotly.express as px
import faicons as fa
from ipyleaflet import Map, Marker, basemaps
import geocoder

df01 = pd.read_csv('peaks.csv').rename(columns={'Metres': 'Meters'})
df01['Note'] = df01['Range'].str.strip().str.cat(df01['Location'].str.strip(), sep=' ', na_rep='')

# Title
ui.page_opts(title='MyPeaks', fillable=True)

# Icons
github_icon = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>')
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
    ui.input_dark_mode(mode="light")

# Main content
with ui.nav_panel("Plot"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
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
        scatter.update_traces(marker=dict(size=30), marker_symbol='triangle-up')
        scatter.update_layout(xaxis_title='', font=dict(size=18), modebar_remove=['resetScale', 'lasso2d', 'select2d'])
        return scatter

with ui.nav_panel("Map"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            'Peaks'
            @render.text
            def peak_names_map():
                if input.radio.get() == 'Specify':
                    selected_peaks = input.selectize()
                    return ', '.join(selected_peaks)
                elif input.radio.get() == 'Top-list':
                    return 'Top-List'
                else:
                    return None
                
    @render_widget
    def map():
        m = Map(basemap=basemaps.Esri.NatGeoWorldMap, zoom=2, center=(27.986065, 86.922623), scroll_wheel_zoom=True)

        if input.radio.get() == 'Specify':
            for mountain in input.selectize():
                g = geocoder.arcgis(mountain)
                latlng = (g.lat, g.lng)
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add(marker)
        elif input.radio.get() == 'Top-list':
            df02 = df01.iloc[(input.begin_list() - 1):input.end_list()]
            for mountain in df02['Mountain']:
                g = geocoder.arcgis(mountain)
                latlng = (g.lat, g.lng)
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add(marker)
            
        return m

with ui.nav_control():
    ui.a(
        github_icon,
        href="https://github.com/mathiselling/peak-app",
        target="_blank",
    )