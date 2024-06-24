import pandas as pd
from shiny import render, reactive
from shiny.express import ui, input
from shinywidgets import render_plotly, render_widget
import plotly.express as px
import faicons as fa
from ipyleaflet import Map, Marker, basemaps
import io
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap

df01 = pd.read_csv("peaks2.csv").rename(columns={"Metres": "Meters"})
df01["Meters"] = df01["Meters"].astype(int)
df01["latlng"] = df01["latlng"].apply(
    lambda x: tuple(map(float, x.strip("[]").split(", "))) if isinstance(x, str) else x
)

# Title
ui.page_opts(title="MyPeaks", fillable=True)

# Icons
github_icon = fa.icon_svg("github", width="24px", height="24px", fill="black")
mountain_icon = fa.icon_svg("mountain")
arrow_up_icon = fa.icon_svg("arrow-up")
plus_icon = fa.icon_svg("plus")
list_icon = fa.icon_svg("list-ul")

# Push nav_panel to the right
ui.nav_spacer()

# Sidebar
with ui.sidebar(open="open"):
    ui.markdown(
        """
        The main purpose of this web application is to give you an overview of the mountains you have climbed in your life.

        Of course, you can also explore other mountains or the top-list of the fourteen 8000m peaks.

        **You choose:**
        """
    )
    ui.input_radio_buttons(
        "radio",
        "",
        ["Select mountains", "Top-list"],
    )
    with ui.panel_conditional('input.radio === "Select mountains"'):
        mountain_options = df01["Mountain"].unique().tolist()
        ui.input_selectize(
            "selectize",
            "Select mountains below or start writing:",
            {option: option for option in mountain_options},
            multiple=True,
        )
    with ui.panel_conditional('input.radio === "Top-list"'):
        ui.input_numeric("begin_list", "Start of the list", 1, min=1, max=1645)
        ui.input_numeric("end_list", "End of the list", 14, min=1, max=1645)

# Main content
with ui.nav_panel("Map"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            "Mountains"

            @render.text
            def peak_names_map():
                if input.radio.get() == "Select mountains":
                    return ", ".join(input.selectize())
                elif input.radio.get() == "Top-list":
                    return "Top-List"
                else:
                    return None

    @render_widget
    def map():
        m = Map(
            basemap=basemaps.Esri.NatGeoWorldMap,
            zoom=2,
            center=(27.986065, 86.922623),
            scroll_wheel_zoom=True,
        )

        if input.radio.get() == "Select mountains":
            for mountain in input.selectize():
                latlng = df01.loc[df01["Mountain"] == mountain, "latlng"].iloc[0]
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add_layer(marker)
        elif input.radio.get() == "Top-list":
            for mountain in df01["Mountain"].iloc[
                (input.begin_list() - 1) : input.end_list()
            ]:
                latlng = df01.loc[df01["Mountain"] == mountain, "latlng"].iloc[0]
                marker = Marker(location=latlng, draggable=False, title=mountain)
                m.add(marker)

        return m


with ui.nav_panel("Plot"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=mountain_icon):
            "Mountains"

            @render.text
            def peak_names_plot():
                if input.radio.get() == "Select mountains":
                    return ", ".join(input.selectize())
                elif input.radio.get() == "Top-list":
                    return "Top-List"
                else:
                    return None

    @render_plotly
    def plot():
        if input.radio.get() == "Select mountains":
            df02 = df01[df01["Mountain"].isin(input.selectize())]
        elif input.radio.get() == "Top-list":
            df02 = df01.iloc[(input.begin_list() - 1) : input.end_list()]
        else:
            df02 = pd.DataFrame(columns=df01.columns)

        scatter = px.scatter(
            df02, x="Mountain", y="Meters", hover_data=["Feet", "Note"]
        )
        scatter.update_traces(marker=dict(size=30), marker_symbol="triangle-up")
        scatter.update_layout(
            xaxis_title="",
            font=dict(size=18),
            modebar_remove=["resetScale", "lasso2d", "select2d"],
        )
        return scatter


with ui.nav_panel("Stats"):
    with ui.layout_columns(fill=False, col_widths=(6, 6, 6)):
        with ui.value_box(showcase=arrow_up_icon):
            "Highest altitude reached"

            @render.text
            def highest_mountain():
                if input.radio.get() == "Select mountains":
                    df02 = df01[df01["Mountain"].isin(input.selectize())]
                elif input.radio.get() == "Top-list":
                    df02 = df01.iloc[(input.begin_list() - 1) : input.end_list()]
                else:
                    df02 = pd.DataFrame(columns=df01.columns)

                highest_mountain = (
                    df02["Meters"].max() if not df02["Meters"].empty else 0
                )

                return f"{highest_mountain:,} m"

        with ui.value_box(showcase=plus_icon):
            "Total height of the mountains"

            @render.text
            def sum_height():
                if input.radio.get() == "Select mountains":
                    df02 = df01[df01["Mountain"].isin(input.selectize())]
                elif input.radio.get() == "Top-list":
                    df02 = df01.iloc[(input.begin_list() - 1) : input.end_list()]
                else:
                    df02 = pd.DataFrame(columns=df01.columns)

                sum_height = df02["Meters"].sum()

                return f"{sum_height:,} m"

        with ui.value_box(showcase=list_icon):
            "Number of mountains"

            @render.text
            def number_mountains():
                if input.radio.get() == "Select mountains":
                    df02 = df01[df01["Mountain"].isin(input.selectize())]
                elif input.radio.get() == "Top-list":
                    df02 = df01.iloc[(input.begin_list() - 1) : input.end_list()]
                else:
                    df02 = pd.DataFrame(columns=df01.columns)

                number_mountains = len(df02)

                return f"{number_mountains}"


with ui.nav_panel("Download Report"):
    with ui.layout_columns(fill=False, col_widths=(12, 4)):
        ui.markdown(
            "If you are interested in a report containing all the mountains and additional information, you can download it here."
        )

        @render.download(label="Download Report", filename="report_mypeaks.pdf")
        async def export():
            if input.radio.get() == "Select mountains":
                df02 = df01[df01["Mountain"].isin(input.selectize())]
            elif input.radio.get() == "Top-list":
                df02 = df01.iloc[(input.begin_list() - 1) : input.end_list()]
            else:
                df02 = pd.DataFrame(columns=df01.columns)

            with io.BytesIO() as buffer:
                with PdfPages(buffer) as pdf:
                    # Add map to PDF
                    worldmap = plt.figure(figsize=(12, 8))

                    m = Basemap(
                        projection="cyl",
                        llcrnrlat=-60,
                        urcrnrlat=90,
                        llcrnrlon=-180,
                        urcrnrlon=180,
                        resolution="c",
                    )

                    m.drawcoastlines()
                    m.drawcountries()
                    m.shadedrelief(scale=0.2)

                    # Plot the coordinates
                    for lat, lon in df02["latlng"]:
                        x, y = m(lon, lat)
                        plt.plot(x, y, "r^", markersize=10)

                    plt.title("World Map with Markers")

                    pdf.savefig(worldmap)
                    plt.close(worldmap)

                    # Add table to PDF
                    df03 = df02.drop(
                        columns=["Unnamed: 0", "Range", "Location", "latlng"],
                    )
                    num_rows = df03.shape[0]
                    column_widths = [2, 1, 1, 4]
                    total_width = sum(column_widths) * 2
                    print(f"number rows: {num_rows}")

                    fig, ax = plt.subplots(figsize=(total_width, num_rows * 0.5))
                    ax.axis("tight")
                    ax.axis("off")
                    table = ax.table(
                        cellText=df03.values,
                        colLabels=df03.columns,
                        cellLoc="left",
                        loc="center",
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(11)

                    # Set column widths
                    for col_idx, width in enumerate(column_widths):
                        for row_idx in range(num_rows + 1):  # +1 to include header
                            cell = table[row_idx, col_idx]
                            cell.set_width((width * 2) / total_width)
                            cell.set_height(0.05)

                    pdf.savefig(fig)
                    plt.close(fig)

                buffer.seek(0)
                yield buffer.read()


with ui.nav_control():
    ui.a(
        github_icon,
        href="https://github.com/mathiselling/peak-app",
        target="_blank",
    )
