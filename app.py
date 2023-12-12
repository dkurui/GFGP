import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output, ClientsideFunction, State

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_table import DataTable
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
import openai
import dash_daq as daq
import plotly.express as px


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)
app.title = "GFGP Analysis Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
# old
df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv.gz"))
dataset = pd.read_csv(DATA_PATH.joinpath("final_clean_busara.csv"))

# NEW
dataframe = pd.read_csv(DATA_PATH.joinpath("CleanedGFGP.csv"))  # NEW

# ------------------------------------

# OLD
country_list = list(dataframe["Country"].unique())  # NEW
institutions_list = list(dataframe["Name of institution"].unique())
country_list.insert(0, 'All Countries')
inst_type_list = list(dataset["Type of institution"].unique())
inst_type_list.insert(0, 'All Institution Types')


# NEW
list_of_countries = list(dataframe["Country"].unique())
list_of_countries.insert(0, 'All Countries')
# ------------------------------------

mapbox_access_token = 'pk.eyJ1Ijoic21hdHRoZXdzOTUiLCJhIjoiY2tnOXZ6bHI2MDE3YTJybXVnZTlmZHQ2aiJ9.4-K3Y_0bc4Z-KJVwNn-TkA'

main_map_layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Incident Map",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=0, lat=0),
        zoom=0.9,
    ),
)

# Countries
countries = ['Algeria',
             'Angola',
             'Benin',
             'Botswana',
             'Burkina Faso',
             'Burundi',
             'Cameroon',
             'Cape Verde',
             'Central African Republic',
             'Chad',
             'Comoros',
             'Democratic Republic of the Congo',
             'Djibouti',
             'Egypt',
             'Equatorial Guinea',
             'Eritrea',
             'Eswatini',
             'Ethiopia',
             'Gabon',
             'Ghana',
             'Guinea',
             'Guinea-Bissau',
             'Ivory Coast',
             'Kenya',
             'Lesotho',
             'Liberia',
             'Libya',
             'Madagascar',
             'Malawi',
             'Mali',
             'Mauritania',
             'Mauritius',
             'Morocco',
             'Mozambique',
             'Namibia',
             'Niger',
             'Nigeria',
             'Republic of the Congo',
             'Rwanda',
             'Sao Tome and Pri­ncipe',
             'Senegal',
             'Seychelles',
             'Sierra Leone',
             'Somalia',
             'South Africa',
             'South Sudan',
             'Sudan',
             'Tanzania',
             'The Gambia',
             'Togo',
             'Tunisia',
             'Uganda',
             'Zambia',
             'Zimbabwe']


df["Admit Source"] = df["Admit Source"].fillna("Not Identified")
admit_list = df["Admit Source"].unique().tolist()

# Date
# Format checkin Time
df["Check-In Time"] = df["Check-In Time"].apply(
    lambda x: dt.strptime(x, "%Y-%m-%d %I:%M:%S %p")
)  # String -> Datetime

# Insert weekday and hour of checkin time
df["Days of Wk"] = df["Check-In Hour"] = df["Check-In Time"]
df["Days of Wk"] = df["Days of Wk"].apply(
    lambda x: dt.strftime(x, "%A")
)  # Datetime -> weekday string

df["Check-In Hour"] = df["Check-In Hour"].apply(
    lambda x: dt.strftime(x, "%I %p")
)  # Datetime -> int(hour) + AM/PM

day_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


# Register all departments for callbacks
all_departments = df["Department"].unique().tolist()
wait_time_inputs = [
    Input((i + "_wait_time_graph"), "selectedData") for i in all_departments
]
score_inputs = [Input((i + "_score_graph"), "selectedData")
                for i in all_departments]


def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H4("Good Financial Grant Practices"),
            html.H5("GFGP Assessment Dashboard"),

            html.Div(
                id="intro",
                children="Explore Institutions Assessment. You can filter your Institutions by country to view their assessments.",
            ),
            html.P('Total number of Intsitutions:', style={'display': 'inline-block',
                                                           'font-size': '18px', 'font-weight': 'bold', 'text-align': 'center'}),
            html.P(id='total-institutions', style={'color': '#FF7F00', 'display': 'inline-block',
                                                   'font-weight': 'bold',  'font-size': '25px', 'text-align': 'center', 'margin-left': '1rem'}),
            html.Hr(),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Filter by Country"),
            dcc.Dropdown(
                id="selected-country",
                options=[{"label": i, "value": i} for i in list_of_countries],
                value=country_list[0],
            ),


            html.Br(),
            html.Br(),
            html.Br(),
            html.Div(
                id="explanation",
                children="The instituions displayed in the dropdown below is based on the country selected. If no country is selected, all institutions shall be displayed", style={'font-size': '12px', 'font-style': 'italic'}),
            html.P("SELECT INSTITUTION TO EXPLORE ITS DETAILS"),

            dcc.Dropdown(
                id="institutions_selected",
                value=institutions_list[0],
                # options=[],
                multi=False,

            ),
            html.Br(),




            html.Br(),
            # html.P("Select Clinic"),
            # dcc.Dropdown(
            #     id="clinic-select",
            #     options=[{"label": i, "value": i} for i in clinic_list],
            #     value=clinic_list[0],
            # ),
            # html.Br(),
            # html.P("Select Check-In Time"),
            # dcc.DatePickerRange(
            #     id="date-picker-select",
            #     start_date=dt(2014, 1, 1),
            #     end_date=dt(2014, 1, 15),
            #     min_date_allowed=dt(2014, 1, 1),
            #     max_date_allowed=dt(2014, 12, 31),
            #     initial_visible_month=dt(2014, 1, 1),
            # ),
            # html.Br(),
            # html.Br(),
            # html.P("Select Admit Source"),
            # dcc.Dropdown(
            #     id="admit-select",
            #     options=[{"label": i, "value": i} for i in admit_list],
            #     value=admit_list[:],
            #     multi=True,
            # ),
            # html.Br(),
            # html.Div(
            #     id="reset-btn-outer",
            #     children=html.Button(
            #         id="reset-btn", children="Reset", n_clicks=0),
            # ),
        ],
    )


def generate_patient_volume_heatmap(start, end, clinic, hm_click, admit_type, reset):
    """
    :param: start: start date from selection.
    :param: end: end date from selection.
    :param: clinic: clinic from selection.
    :param: hm_click: clickData from heatmap.
    :param: admit_type: admission type from selection.
    :param: reset (boolean): reset heatmap graph if True.

    :return: Patient volume annotated heatmap.
    """

    filtered_df = df[
        (df["Clinic Name"] == clinic) & (df["Admit Source"].isin(admit_type))
    ]
    filtered_df = filtered_df.sort_values("Check-In Time").set_index("Check-In Time")[
        start:end
    ]

    x_axis = [datetime.time(i).strftime("%I %p")
              for i in range(24)]  # 24hr time list
    y_axis = day_list

    hour_of_day = ""
    weekday = ""
    shapes = []

    if hm_click is not None:
        hour_of_day = hm_click["points"][0]["x"]
        weekday = hm_click["points"][0]["y"]

        # Add shapes
        x0 = x_axis.index(hour_of_day) / 24
        x1 = x0 + 1 / 24
        y0 = y_axis.index(weekday) / 7
        y1 = y0 + 1 / 7

        shapes = [
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                line=dict(color="#ff6347"),
            )
        ]

    # Get z value : sum(number of records) based on x, y,

    z = np.zeros((7, 24))
    annotations = []

    for ind_y, day in enumerate(y_axis):
        filtered_day = filtered_df[filtered_df["Days of Wk"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_record = filtered_day[filtered_day["Check-In Hour"] == x_val][
                "Number of Records"
            ].sum()
            z[ind_y][ind_x] = sum_of_record

            annotation_dict = dict(
                showarrow=False,
                text="<b>" + str(sum_of_record) + "<b>",
                xref="x",
                yref="y",
                x=x_val,
                y=day,
                font=dict(family="sans-serif"),
            )
            # Highlight annotation text by self-click
            if x_val == hour_of_day and day == weekday:
                if not reset:
                    annotation_dict.update(size=15, font=dict(color="#ff6347"))

            annotations.append(annotation_dict)

    # Heatmap
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z} Patient Records"

    data = [
        dict(
            x=x_axis,
            y=y_axis,
            z=z,
            type="heatmap",
            name="",
            hovertemplate=hovertemplate,
            showscale=False,
            colorscale=[[0, "#caf3ff"], [1, "#2c82ff"]],
        )
    ]

    layout = dict(
        margin=dict(l=70, b=50, t=50, r=50),
        modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        annotations=annotations,
        shapes=shapes,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" "
        ),
        hovermode="closest",
        showlegend=False,
    )
    return {"data": data, "layout": layout}


def generate_table_row(id, style, col1, col2, col3):
    """ Generate table rows.

    :param id: The ID of table row.
    :param style: Css style of this row.
    :param col1 (dict): Defining id and children for the first column.
    :param col2 (dict): Defining id and children for the second column.
    :param col3 (dict): Defining id and children for the third column.
    """

    return html.Div(
        id=id,
        className="row table-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                style={"display": "table", "height": "100%"},
                className="two columns row-department",
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center", "height": "100%"},
                className="five columns",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"textAlign": "center", "height": "100%"},
                className="five columns",
                children=col3["children"],
            ),
        ],
    )


def generate_table_row_helper(department):
    """Helper function.

    :param: department (string): Name of department.
    :return: Table row.
    """
    return generate_table_row(
        department,
        {},
        {"id": department + "_department", "children": html.B(department)},
        {
            "id": department + "wait_time",
            "children": dcc.Graph(
                id=department + "_wait_time_graph",
                style={"height": "100%", "width": "100%"},
                className="wait_time_graph",
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure={
                    "layout": dict(
                        margin=dict(l=0, r=0, b=0, t=0, pad=0),
                        xaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        yaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                },
            ),
        },
        {
            "id": department + "_patient_score",
            "children": dcc.Graph(
                id=department + "_score_graph",
                style={"height": "100%", "width": "100%"},
                className="patient_score_graph",
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure={
                    "layout": dict(
                        margin=dict(l=0, r=0, b=0, t=0, pad=0),
                        xaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        yaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                },
            ),
        },
    )


def initialize_table():
    """
    :return: empty table children. This is intialized for registering all figure ID at page load.
    """

    # header_row
    header = [
        generate_table_row(
            "header",
            {"height": "50px"},
            {"id": "header_department", "children": html.B("Department")},
            {"id": "header_wait_time_min",
                "children": html.B("Wait Time Minutes")},
            {"id": "header_care_score", "children": html.B("Care Score")},
        )
    ]

    # department_row
    rows = [generate_table_row_helper(department)
            for department in all_departments]
    header.extend(rows)
    empty_table = header

    return empty_table


def generate_patient_table(figure_list, departments, wait_time_xrange, score_xrange):
    """
    :param score_xrange: score plot xrange [min, max].
    :param wait_time_xrange: wait time plot xrange [min, max].
    :param figure_list:  A list of figures from current selected metrix.
    :param departments:  List of departments for making table.
    :return: Patient table.
    """
    # header_row
    header = [
        generate_table_row(
            "header",
            {"height": "50px"},
            {"id": "header_department", "children": html.B("Department")},
            {"id": "header_wait_time_min",
                "children": html.B("Wait Time Minutes")},
            {"id": "header_care_score", "children": html.B("Care Score")},
        )
    ]

    # department_row
    rows = [generate_table_row_helper(department)
            for department in departments]
    # empty_row
    empty_departments = [
        item for item in all_departments if item not in departments]
    empty_rows = [
        generate_table_row_helper(department) for department in empty_departments
    ]

    # fill figures into row contents and hide empty rows
    for ind, department in enumerate(departments):
        rows[ind].children[1].children.figure = figure_list[ind]
        rows[ind].children[2].children.figure = figure_list[ind +
                                                            len(departments)]
    for row in empty_rows[1:]:
        row.style = {"display": "none"}

    # convert empty row[0] to axis row
    empty_rows[0].children[0].children = html.B(
        "graph_ax", style={"visibility": "hidden"}
    )

    empty_rows[0].children[1].children.figure["layout"].update(
        dict(margin=dict(t=-70, b=50, l=0, r=0, pad=0))
    )

    empty_rows[0].children[1].children.config["staticPlot"] = True

    empty_rows[0].children[1].children.figure["layout"]["xaxis"].update(
        dict(
            showline=True,
            showticklabels=True,
            tick0=0,
            dtick=20,
            range=wait_time_xrange,
        )
    )
    empty_rows[0].children[2].children.figure["layout"].update(
        dict(margin=dict(t=-70, b=50, l=0, r=0, pad=0))
    )

    empty_rows[0].children[2].children.config["staticPlot"] = True

    empty_rows[0].children[2].children.figure["layout"]["xaxis"].update(
        dict(showline=True, showticklabels=True,
             tick0=0, dtick=0.5, range=score_xrange)
    )

    header.extend(rows)
    header.extend(empty_rows)
    return header


def create_table_figure(
    department, filtered_df, category, category_xrange, selected_index
):
    """Create figures.

    :param department: Name of department.
    :param filtered_df: Filtered dataframe.
    :param category: Defining category of figure, either 'wait time' or 'care score'.
    :param category_xrange: x axis range for this figure.
    :param selected_index: selected point index.
    :return: Plotly figure dictionary.
    """
    aggregation = {
        "Wait Time Min": "mean",
        "Care Score": "mean",
        "Days of Wk": "first",
        "Check-In Time": "first",
        "Check-In Hour": "first",
    }

    df_by_department = filtered_df[
        filtered_df["Department"] == department
    ].reset_index()
    grouped = (
        df_by_department.groupby("Encounter Number").agg(
            aggregation).reset_index()
    )
    patient_id_list = grouped["Encounter Number"]

    x = grouped[category]
    y = list(department for _ in range(len(x)))

    def f(x_val): return dt.strftime(x_val, "%Y-%m-%d")
    check_in = (
        grouped["Check-In Time"].apply(f)
        + " "
        + grouped["Days of Wk"]
        + " "
        + grouped["Check-In Hour"].map(str)
    )

    text_wait_time = (
        "Patient # : "
        + patient_id_list
        + "<br>Check-in Time: "
        + check_in
        + "<br>Wait Time: "
        + grouped["Wait Time Min"].round(decimals=1).map(str)
        + " Minutes,  Care Score : "
        + grouped["Care Score"].round(decimals=1).map(str)
    )

    layout = dict(
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        clickmode="event+select",
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=category_xrange,
        ),
        yaxis=dict(
            showgrid=False, showline=False, showticklabels=False, zeroline=False
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    trace = dict(
        x=x,
        y=y,
        mode="markers",
        marker=dict(size=14, line=dict(width=1, color="#ffffff")),
        color="#2c82ff",
        selected=dict(marker=dict(color="#ff6347", opacity=1)),
        unselected=dict(marker=dict(opacity=0.1)),
        selectedpoints=selected_index,
        hoverinfo="text",
        customdata=patient_id_list,
        text=text_wait_time,
    )

    return {"data": [trace], "layout": layout}


app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url(
                "APHRC-logo.png"), style={'height': '5rem'})],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ], style={'width': '23%'}
        ),
        # Right column
        html.Div(
            id="right-column",
            style={'height': '90vh', 'overflow': 'scroll',
                   'width': '72%'},
            className="eight columns",
            children=[
                # Patient Volume Heatmap
                html.Div(
                    id="institutions_card",
                    children=[
                        html.B("INSTITUTIONS RANKING"),
                        html.Hr(),

                        html.P('Country: ', style={
                            'display': 'inline-block', 'font-size': '15px'}),
                        html.P(id='country_output', style={'display': 'inline-block', 'color': '#FF7F00',
                                                           'font-weight': 'bold',  'font-size': '15px', 'text-align': 'center', 'margin-left': '1rem'}),


                        html.P(id='institution_output', style={'display': 'inline-block', 'color': '#FF7F00',
                                                               'font-weight': 'bold', 'font-size': '15px',  'text-align': 'center', 'margin-left': '1rem'}),


                    ],

                ),

                dbc.Row([

                    dbc.Col([
                        dbc.Card([

                            html.Div(id='gs_plats', style={
                                'color': 'darkviolet', 'font-weight': 'bold', 'font-size': '10px', 'text-align': 'center'}),
                            dbc.CardBody(
                                [
                                    html.Div(
                                        id='institutions',

                                    ),

                                ]

                            ),
                        ], style={'border': 'none'}),

                    ],  style={
                        'height': '26rem',
                        'overflowY': 'auto',
                        'font-size': '12px',
                        'line-height': '1',
                        'width': '80%',
                    }),
                    dbc.Col([
                        dbc.Card([

                            html.Div(
                                 id="top",
                                 className="top",
                                 children=[html.Img(src=app.get_asset_url(
                                     "top_uni.png"), style={'height': '10rem', 'text-align': 'center'})], style={'text-align': 'center', 'margin-top': '3rem'}
                                 ),

                            html.P('TOP INSTITUTION', style={
                                'font-size': '18px', 'font-weight': 'bold', 'text-align': 'center'}),
                            html.P(id='top-institution', style={'color': '#FF7F00',
                                                                'font-weight': 'bold',  'font-size': '25px', 'text-align': 'center', 'margin-left': '1rem'}),



                            html.P(id='top-institution-country', style={'color': 'black',
                                                                        'font-weight': 'bold',  'font-size': '12px', 'text-align': 'center', 'margin-top': '3rem'}),



                        ], style={'border': 'none'}),

                    ], style={
                        'height': '26rem',
                        'overflowY': 'auto',

                        'font-size': '11px',
                        'line-height': '1',

                        'width': '20%',
                    }),

                ], style={'display': 'flex'}),
                html.Hr(),


                # Patient Volume Heatmap
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.B("INSTITUTIONS PER COUNTRY"),
                        html.Hr(),
                        # dcc.Graph(id="patient_volume_hm"),
                        # dbc.Spinner(children=[
                        #     dcc.Graph(id='country-bubble-chart',
                        #               style={'height': '70vh'}, config={'displayModeBar': False},
                        #               figure={'layout': {'plot_bgcolor': 'lightgray'}})], size="lg", color="success", type="border", fullscreen=False, spinner_style={'width': '6rem', 'height': '6rem'}),

                        dcc.Interval(
                            id='interval-component',
                            # Update every hour (adjust as needed)
                            interval=1000 * 60*60,
                            n_intervals=0
                        ),
                        dbc.Spinner(children=[
                            dcc.Graph(id='country_graph',
                                      style={'height': '40vh',
                                             'autosize': 'true'},
                                      figure={'layout': {'plot_bgcolor': 'lightgray'}})], size="lg", color="success", type="border", fullscreen=True, spinner_style={'width': '6rem', 'height': '6rem'}),


                    ],
                ),

                html.Br(),
                html.Br(),
                # INSTITUTION SCORES
                html.Div(
                    id="inst_scores",
                    children=[
                        html.B("INSTITUTION'S DETAILS "),
                        html.Hr(),
                        html.P(id='inst_in_quest', style={
                            'font-size': '18px', 'font-weight': 'bold', 'text-align': 'left', 'color': '#022896'}),

                        html.P(id='country_in_quest', style={
                            'font-size': '18px', 'font-weight': 'bold', 'text-align': 'left', 'color': '#022896'}),
                        html.Hr(),

                        # INSTITUTION DEPARTMENTS
                        html.Div(
                            id="inst_depts",
                            children=[
                                html.Div(id="per_deps",
                                         children=[
                                             html.Div(
                                                 id="assessment_level",
                                                 className="top",
                                                 children=[
                                                     html.P("GFGP Assessment Level", style={
                                                         'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),

                                                 ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                                             html.Div(
                                                 id="medical",
                                                 className="top",
                                                 children=[
                                                     html.P('GFGP Self Assessment Score', style={
                                                         'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),

                                                 ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                                             html.Div(
                                                 id="socialogy",
                                                 className="top",
                                                 children=[
                                                     html.P("KPMG's due diligence overall score", style={
                                                         'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                                                     html.P(id='socialogy_dept', style={
                                                         'font-size': '15px', 'font-weight': 'bold', 'text-align': 'center', 'margin-top': '0rem'})
                                                 ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),


                                         ], style={'display': 'inline-flex', 'width': '100%'}),], style={'text-align': 'center'},
                        ),

                        html.Hr(),

                        html.Div(id="scores_guages",
                                 children=[
                                     html.Div(
                                         id="input_scores_",
                                         className="top",
                                         children=[
                                             html.P(id='gfgp_assessment_level', style={
                                                 'font-size': '18px', 'font-weight': 'bold', 'text-align': 'center', 'color': '#022896'}),



                                         ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                                     html.Div(
                                         id="output_scores_",
                                         className="top",
                                         children=[

                                             daq.Gauge(
                                                 id="gfgp_self_assessment_score",
                                                 max=1,
                                                 min=0,
                                                 showCurrentValue=True,  # default size 200 pixel
                                                 size=150

                                             ),

                                         ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                                     html.Div(
                                         id="impact_scores",
                                         className="top",
                                         children=[

                                             daq.Gauge(
                                                 id="kpmg_due_dilligence_score",
                                                 max=1,
                                                 min=0,
                                                 showCurrentValue=True,  # default size 200 pixel
                                                 size=150,



                                             )

                                         ], style={'width': '33.3%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                                 ], style={'display': 'inline-flex', 'width': '100%'}),], style={'background': 'white'}
                ),
                html.Hr(),

                # COMPARE INSTITUTIONS


                # html.Div(
                #     id="wait_time_card",
                #     children=[
                #         html.B("COMPARE INSTITUTIONS"),
                #         html.Hr(),
                #         dbc.Row([
                #             dbc.Col([
                #                 dbc.Card([
                #                     html.Div(id='comps', style={
                #                         'color': 'darkviolet', 'font-weight': 'bold', 'font-size': '10px', 'text-align': 'center'}),
                #                     dbc.CardBody(
                #                         [
                #                             html.Div(
                #                                 id='comparison',
                #                                 children=[

                #                                     dbc.CardBody(
                #                                         [
                #                                             html.P(
                #                                                 "Select First Institution"),

                #                                             dcc.Dropdown(
                #                                                 id="selected-institution_one",
                #                                                 options=[{"label": i, "value": i}
                #                                                          for i in institutions_list],
                #                                                 value=institutions_list[0],
                #                                             )], style={'width': '100%'}),
                #                                     html.Br(),
                #                                     html.Br(),
                #                                     dbc.CardBody(
                #                                         [
                #                                             html.P(
                #                                                 "Select Second Institution "),
                #                                             dcc.Dropdown(
                #                                                 id="selected-institution_two",
                #                                                 options=[{"label": i, "value": i}
                #                                                          for i in institutions_list],
                #                                                 value=institutions_list[1],
                #                                             )], style={'width': '100%'}),
                #                                 ], style={'width': '-webkit-fill-available', 'margin-top': '2rem'}

                #                             ),

                #                         ]

                #                     ),
                #                 ], style={'border': 'none'}),

                #             ],  style={
                #                 'height': '26rem',
                #                 'overflowY': 'auto',
                #                 'font-size': '12px',
                #                 'line-height': '1',
                #                 'width': '20%',
                #             }),
                #             dbc.Col([
                #                 dbc.Card([

                #                     html.Div(
                #                         id="top_uni",
                #                         className="top",
                #                         children=[
                #                             # html.P(id='comparison_figure', style={
                #                             #        'color': '#FF7F00', 'font-weight': 'bold',  'font-size': '25px', 'text-align': 'center', 'margin-left': '1rem'}),

                #                             dbc.Spinner(children=[
                #                                 dcc.Graph(id='comparison_figure',
                #                                           style={'height': '40vh',
                #                                                  'autosize': 'true'},
                #                                           figure={'layout': {'plot_bgcolor': 'lightgray'}})], size="lg", color="success", type="border", fullscreen=True, spinner_style={'width': '6rem', 'height': '6rem'}),
                #                         ],

                #                         style={'text-align': 'center',
                #                                'margin-top': '3rem'}

                #                     ),
                #                 ], style={'border': 'none'}),

                #             ], style={
                #                 'font-size': '11px',
                #                 'width': '80%',
                #             }),

                #         ], style={'display': 'flex'}),


                #     ],
                # ),

                # # VISUALIZATIONS
                # html.Div(
                #     id="inst_viz",
                #     children=[

                #         html.Div(
                #             html.B("TOP INSTITUTIONS"), style={
                #                 'text-align': 'center'}),
                #         html.Hr(),

                #         # OUTPUT INSTITUTIONS
                #         html.Div(id="scores",
                #                  children=[
                #                      html.Div(
                #                          id="input_scores",
                #                          className="top",
                #                          children=[
                #                              html.P('TOP INPUT SCORE INSTITUTIONS ', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                             html.P([
                #                                 'Staff capacity to perform, and apply research, research insfrastructure'
                #                             ],
                #                                  style={'font-size': '11px', 'font-style': 'italic',  'text-align': 'center', 'margin-top': '0rem'}),
                #                              html.Hr(),
                #                              html.Div(
                #                                  id='top-input-score-institutions', style={

                #                                      'overflowY': 'auto',
                #                                      'font-size': '12px',
                #                                      'line-height': '1',

                #                                  }
                #                              ),




                #                          ], style={'width': '25%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                #                      html.Div(
                #                          id="output_scores",
                #                          className="top",
                #                          children=[
                #                              html.P('OUTPUT SCORE TOP INSTITUTIONS', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                              html.P([
                #                                  'Research,Collaborations and Grants and Donations Management '
                #                              ],
                #                                  style={'font-size': '11px', 'font-style': 'italic', 'text-align': 'center', 'margin-top': '0rem'}),
                #                             html.Hr(),
                #                              html.Div(
                #                                  id='top-output-score-institutions', style={

                #                                      'overflowY': 'auto',
                #                                      'font-size': '12px',
                #                                      'line-height': '1',

                #                                  }
                #                              ),
                #                          ], style={'width': '25%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                #                      html.Div(
                #                          id="impact_scores_",
                #                          className="top",
                #                          children=[
                #                              html.P('IMPACT SCORE TOP INSTITUTIONS', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                              html.P([
                #                                  'Equal opportunity policies, dissemination of research evidence of influence in policy and strategy ',
                #                                  html.Br(),  # Add another line break

                #                              ],
                #                                  style={'font-size': '11px', 'font-style': 'italic', 'text-align': 'center', 'margin-top': '0rem'}),
                #                              html.Hr(),
                #                              html.Div(
                #                                  id='top-impact-score-institutions',  style={

                #                                      'overflowY': 'auto',
                #                                      'font-size': '12px',
                #                                      'line-height': '1rem',

                #                                  }
                #                              ),
                #                          ], style={'width': '25%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                #                      html.Div(
                #                          id="overall_scores_",
                #                          className="top",
                #                          children=[
                #                              html.P('OVERALL SCORE TOP INSTITUTIONS', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                              html.P([
                #                                  'Best perfomring institutions in the aggregated overall score (input, output and impact score)',
                #                                  html.Br(),  # Add another line break

                #                              ],
                #                                  style={'font-size': '11px', 'text-align': 'center', 'margin-top': '0rem'}),
                #                             html.Hr(),
                #                              html.Div(
                #                                  id='top-overall-score-institutions', style={

                #                                      'overflowY': 'auto',
                #                                      'font-size': '12px',
                #                                      'line-height': '1',

                #                                  }
                #                              ),

                #                          ], style={'width': '25%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                #                  ], style={'display': 'inline-flex', 'width': '100%'}),], style={'background': 'white'}
                # ),
                # html.Br(),


                # html.Div(
                #     id="depts",
                #     children=[
                #         html.Div(
                #             html.B("VISUALIZATION"), style={
                #                 'text-align': 'center'}),
                #         html.Hr(),

                #         # OUTPUT VISUALIZATIONS
                #         html.Div(id="d1",
                #                  children=[
                #                      html.Div(
                #                          id="medics",
                #                          className="top",
                #                          children=[
                #                              html.P('Institutions with Medical Department ', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                             html.Hr(),
                #                             html.P(id='medical-country', style={
                #                                 'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),
                #                              html.P(id='medical-inst', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),

                #                              html.Div(
                #                                  dcc.Graph(
                #                                      id='medical-pie-chart', figure={}),
                #                              ),
                #                          ], style={'width': '50%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                #                      html.Div(
                #                          id="agric",
                #                          className="top",
                #                          children=[
                #                              html.P('Institutions with Agricultural Department', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                              html.Hr(),
                #                              html.P(id='agric-country', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),
                #                              html.P(id='agric-inst', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),

                #                              html.Div(
                #                                  dcc.Graph(
                #                                      id='agri-pie-chart',  figure={}),

                #                              ),
                #                          ], style={'width': '50%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                #                  ], style={'display': 'inline-flex', 'width': '100%'}),], style={'background': 'white'}
                # ),
                # html.Br(),

                # html.Div(
                #     id="depts_two",
                #     children=[

                #         # OUTPUT VISUALIZATIONS
                #         html.Div(id="d2",
                #                  children=[
                #                      html.Div(
                #                          id="medics_",
                #                          className="top",
                #                          children=[
                #                              html.P('Institutions with Socialogy Department ', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                             html.Hr(),
                #                             html.P(id='socialogy-country', style={
                #                                 'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),
                #                              html.P(id='socialogy-inst', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),

                #                              html.Div(
                #                                  dcc.Graph(
                #                                      id='socialogy-pie-chart', figure={}),
                #                              ),
                #                          ], style={'width': '50%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),

                #                      html.Div(
                #                          id="agric_",
                #                          className="top",
                #                          children=[
                #                              html.P('Institutions with Business/Commerce/Economy Department', style={
                #                                  'font-size': '11px', 'font-weight': 'bold', 'text-align': 'center'}),
                #                              html.Hr(),
                #                              html.P(id='business-country', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),
                #                              html.P(id='business-inst', style={
                #                                  'font-size': '11px', 'font-weight': 'italic', 'text-align': 'center'}),

                #                              html.Div(
                #                                  dcc.Graph(
                #                                      id='business-pie-chart',  figure={}),

                #                              ),
                #                          ], style={'width': '50%', 'text-align': '-webkit-center', 'margin-inline': '2rem'}),
                #                  ], style={'display': 'inline-flex', 'width': '100%'}),], style={'background': 'white'}
                # ),
                # html.Hr(),


                # html.Br(),

                # # Score Distributions
                # html.Div(
                #     id="score_distributions",
                #     children=[
                #         html.Div(
                #             children=[
                #                 dcc.Graph(
                #                     id="input_score_normal-distribution-graph", style={'height': '30rem'}),
                #                 html.Hr(),
                #             ], style={'width': '48%', 'heght': '40rem', 'text-align': '-webkit-center', 'margin-inline': '0rem'}
                #         ),
                #         html.Div(
                #             children=[

                #                 html.Hr(),
                #             ], style={'width': '6%', 'heght': '40rem', 'text-align': '-webkit-center', 'margin-inline': '0rem'}
                #         ),


                #         html.Div(
                #             children=[
                #                 dcc.Graph(
                #                     id="output_score_normal-distribution-graph", style={'height': '30rem'}),
                #                 html.Hr(),
                #             ], style={'width': '48%', 'text-align': '-webkit-center', 'margin-inline': '0rem'}

                #         ),
                #     ], style={'display': 'inline-flex', 'width': '100%', 'height': '40rem'},
                # ),
                # # distributions
                # html.Div(
                #     id="score_distributions_2",
                #     children=[
                #         html.Div(
                #             children=[
                #                 dcc.Graph(
                #                     id="impact_score_normal-distribution-graph", style={'height': '30rem'}),
                #                 html.Hr(),
                #             ], style={'width': '48%', 'heght': '40rem', 'text-align': '-webkit-center', 'margin-inline': '0rem'}
                #         ),
                #         html.Div(
                #             children=[

                #                 html.Hr(),
                #             ], style={'width': '6%', 'heght': '40rem', 'text-align': '-webkit-center', 'margin-inline': '0rem'}
                #         ),


                #         html.Div(
                #             children=[
                #                 dcc.Graph(
                #                     id="overall_score_normal-distribution-graph", style={'height': '30rem'}),
                #                 html.Hr(),
                #             ], style={'width': '100%', 'text-align': '-webkit-center', 'margin-inline': '0rem'}

                #         ),
                #     ], style={'display': 'inline-flex', 'width': '100%', 'height': '40rem'},
                # ),
                # html.Br(),
            ],
        ),
    ],
)


# @app.callback(
#     [Output("country_output", "children"),
#      Output("institution_output", "children"),
#      Output("institutions", "children"),
#      Output("top-institution", "children"),
#      Output("top-institution-country", "children"),
#      Output("total-institutions", "children")
#      ],
#     [
#         Input("selected-country", "value"),
#         Input("institution-type", "value"),

#     ],
# )
# def update_heatmap(country, institutiton_type):

#     # df = dataset[dataset["Country"] == country]
#     total_institutions = len(dataset)
#     if str(country) == 'All Countries' or str(country) == 'None':
#         country = 'All Countries'
#         df = dataset
#     else:
#         df = dataset[dataset["Country"] == country]

#     if str(institutiton_type) == 'All Institution Types' or str(institutiton_type) == 'None':
#         institutiton_type = 'All Institution types'
#         df = df
#     else:
#         df = df[df['Type of institution'] == institutiton_type]

#     filtered_data = df.sort_values('SCORE', ascending=False)
#     if (len(filtered_data) > 0):
#         top_institution = filtered_data['Institution Name'].iloc[0]
#         top_inst_country = filtered_data['Country'].iloc[0]

#     else:
#         top_institution = 'None'
#         top_inst_country = ''

#     if country == 'All Countries':
#         top_inst_country = 'COUNTRY: '+top_inst_country
#     else:
#         top_inst_country = ''

#     filtered_data['Number'] = range(1, len(filtered_data) + 1)

#     # Swap the columns in the DataFrame
#     filtered_data = filtered_data[['Number'] +
#                                   list(filtered_data.columns[:-1])]

#     filtered_data = filtered_data[[
#         'Number', 'Institution Name','Self Assessment Score','Assessment Level Score', 'KPMG Due Diligence Overall Score' 'SCORE']]

#     data_table = DataTable(
#         id='data-table',
#         columns=[{"name": col, "id": col} for col in filtered_data.columns],
#         data=filtered_data.to_dict('records'),
#         style_table={},

#         # style_cell_conditional=[

#         #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
#         # ],
#         style_data={
#             'color': 'black',
#             'backgroundColor': 'white',
#             'textAlign': 'left',
#             'font-family': 'sans-serif',
#             'whiteSpace': 'normal'
#         },
#         style_data_conditional=[
#             {'if': {'row_index': 'odd'},
#                 'backgroundColor': 'rgb(220, 220, 220)'},
#             {'if': {'column_id': 'Number'}, 'width': '30px'},
#             {'if': {'column_id': 'Institution Name'}, 'width': '500px'},


#         ],
#         style_header={
#             'backgroundColor': 'rgb(210, 210, 210)',
#             'color': 'black',
#             'fontWeight': 'bold',
#             'textAlign': 'left',
#             'font-family': 'sans-serif',

#         },
#     )

#     global final_table
#     final_table = html.Div(data_table)

#     return country, institutiton_type, final_table, top_institution, top_inst_country, total_institutions


# NEW Method
@app.callback(
    [Output("country_output", "children"),
     Output("institutions", "children"),
     Output("top-institution", "children"),
     Output("top-institution-country", "children"),
     Output("total-institutions", "children")
     ],
    [
        Input("selected-country", "value"),
    ],
)
def update_countryLists(country):
    total_institutions = len(dataframe)
    if str(country) == 'All Countries' or str(country) == 'None':
        country = 'All Countries'
        df = dataframe
    else:
        df = dataframe[dataframe["Country"] == country]

    # Define the custom order for the "assessment" column
    custom_order = ['Platinum', 'Gold', 'Silver', 'Bronze']

    # Convert the "assessment" column to a Categorical data type with the custom order
    df['GFGP Assessment Level'] = pd.Categorical(
        df['GFGP Assessment Level'], categories=custom_order, ordered=True)

    # Sort the DataFrame based on the "assessment" column and then the "KPMG's due diligence overall score" column
    filtered_data = df.sort_values(
        ['GFGP Assessment Level', "KPMG's due diligence overall score"], ascending=[True, False])

    # grouped_data = df.groupby('GFGP Assessment Level')
    # filtered_data = grouped_data.apply(lambda x: x.sort_values(
    #     "KPMG's due diligence overall score", ascending=False))

    # filtered_data = df.sort_values(
    #     "KPMG's due diligence overall score", ascending=False)

    if (len(filtered_data) > 0):
        top_institution = filtered_data['Name of institution'].iloc[0]
        top_inst_country = filtered_data['Country'].iloc[0]

    else:
        top_institution = 'None'
        top_inst_country = ''

    if country == 'All Countries':
        top_inst_country = 'COUNTRY: '+top_inst_country
    else:
        top_inst_country = ''

    filtered_data['Number'] = range(1, len(filtered_data) + 1)

    # Swap the columns in the DataFrame
    filtered_data = filtered_data[['Number'] +
                                  list(filtered_data.columns[:-1])]

    filtered_data = filtered_data[[
        'Number', 'Name of institution', 'GFGP Self-Assessment Score', 'GFGP Assessment Level', "KPMG's due diligence overall score"]]

    data_table = DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in filtered_data.columns],
        data=filtered_data.to_dict('records'),
        style_table={},

        # style_cell_conditional=[

        #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
        # ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'textAlign': 'left',
            'font-family': 'sans-serif',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)'},
            {'if': {'column_id': 'Number'}, 'width': '30px'},
            {'if': {'column_id': 'Institution Name'}, 'width': '500px'},

        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'sans-serif',

        },
    )

    global final_table
    final_table = html.Div(data_table)
    return country, final_table, top_institution, top_inst_country, total_institutions

# TOP INSTITUTIONS TABLES
# INPUT


@app.callback(
    [
        Output("top-input-score-institutions", "children"),
    ],
    [
        Input("selected-country", "value"),

    ],
)
def update_top_input_score_inst(country):
    if str(country) == 'All Countries' or str(country) == 'None':
        country = 'All Countries'
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    filtered_data = df.sort_values(
        'Overall Input Score', ascending=False).head(15)

    filtered_data['Number'] = range(1, len(filtered_data) + 1)

    # Swap the columns in the DataFrame
    filtered_data = filtered_data[['Number'] +
                                  list(filtered_data.columns[:-1])]

    filtered_data = filtered_data[[
        'Number', 'Institution Name', 'Overall Input Score']]
    filtered_data.columns = ['#', 'Institution', 'Score']

    data_table = DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in filtered_data.columns],
        data=filtered_data.to_dict('records'),
        style_table={},

        # style_cell_conditional=[

        #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
        # ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'textAlign': 'left',
            'font-family': 'sans-serif',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
             'backgroundColor': '#FEF0E7'},
            {'if': {'column_id': 'Number'}, 'width': '30px'},
            {'if': {'column_id': 'Institution Name'}, 'width': '500px'},



        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'sans-serif',

        },
    )

    global final_table
    final_table = html.Div(data_table)

    return final_table,

# OUTPUt SCORE


@app.callback(
    [
        Output("top-output-score-institutions", "children"),
    ],
    [
        Input("selected-country", "value"),
    ],
)
def update_top_output_score_inst(country, institutiton_type):
    if str(country) == 'All Countries' or str(country) == 'None':
        country = 'All Countries'
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    filtered_data = df.sort_values(
        'Overall Output Score', ascending=False).head(15)

    filtered_data['Number'] = range(1, len(filtered_data) + 1)

    # Swap the columns in the DataFrame
    filtered_data = filtered_data[['Number'] +
                                  list(filtered_data.columns[:-1])]

    filtered_data = filtered_data[[
        'Number', 'Institution Name', 'Overall Output Score']]
    filtered_data.columns = ['#', 'Institution', 'Score']

    data_table = DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in filtered_data.columns],
        data=filtered_data.to_dict('records'),
        style_table={},

        # style_cell_conditional=[

        #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
        # ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'textAlign': 'left',
            'font-family': 'sans-serif',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
             'backgroundColor': '#FEF0E7'},
            {'if': {'column_id': 'Number'}, 'width': '30px'},
            {'if': {'column_id': 'Institution Name'}, 'width': '500px'},



        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'sans-serif',

        },
    )

    global final_table
    final_table = html.Div(data_table)

    return final_table,

# IMPACT SCORE


@app.callback(
    [
        Output("top-impact-score-institutions", "children"),
    ],
    [
        Input("selected-country", "value"),
    ],
)
def update_top_output_score_inst(country):
    if str(country) == 'All Countries' or str(country) == 'None':
        country = 'All Countries'
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    filtered_data = df.sort_values(
        'Overall Impact Score', ascending=False).head(15)

    filtered_data['Number'] = range(1, len(filtered_data) + 1)

    # Swap the columns in the DataFrame
    filtered_data = filtered_data[['Number'] +
                                  list(filtered_data.columns[:-1])]

    filtered_data = filtered_data[[
        'Number', 'Institution Name', 'Overall Impact Score']]
    filtered_data.columns = ['#', 'Institution', 'Score']

    data_table = DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in filtered_data.columns],
        data=filtered_data.to_dict('records'),
        style_table={},

        # style_cell_conditional=[

        #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
        # ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'textAlign': 'left',
            'font-family': 'sans-serif',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
                'backgroundColor': '#FEF0E7'},
            {'if': {'column_id': 'Number'}, 'width': '30px'},
            {'if': {'column_id': 'Institution Name'}, 'width': '500px'},



        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'sans-serif',

        },
    )

    global final_table
    final_table = html.Div(data_table)

    return final_table,
# OVERALL SCORE


@app.callback(
    [
        Output("top-overall-score-institutions", "children"),
    ],
    [
        Input("selected-country", "value"),
    ],
)
def update_top_output_score_inst(country):
    if str(country) == 'All Countries' or str(country) == 'None':
        country = 'All Countries'
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    filtered_data = df.sort_values(
        'SCORE', ascending=False).head(15)

    filtered_data['Number'] = range(1, len(filtered_data) + 1)

    # Swap the columns in the DataFrame
    filtered_data = filtered_data[['Number'] +
                                  list(filtered_data.columns[:-1])]

    filtered_data = filtered_data[[
        'Number', 'Institution Name', 'SCORE']]
    filtered_data.columns = ['#', 'Institution', 'Score']

    data_table = DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in filtered_data.columns],
        data=filtered_data.to_dict('records'),
        style_table={},

        # style_cell_conditional=[

        #     {'if': {'column_id': 'Number'}, 'width': '3rem'},
        # ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'textAlign': 'left',
            'font-family': 'sans-serif',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'},
                'backgroundColor': '#FEF0E7'},
            {'if': {'column_id': 'Number'}, 'width': '30px'},
            {'if': {'column_id': 'Institution Name'}, 'width': '500px'},



        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'sans-serif',

        },
    )

    global final_table
    final_table = html.Div(data_table)

    return final_table,


app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("wait_time_table", "children")] + wait_time_inputs + score_inputs,
)

# --------------------MAKE INCIDENT HISTOGRAM-----------------------------------


@app.callback(
    Output("country_graph", "figure"),
    Input('interval-component', 'n_intervals'),

)
def make_country_graph(interval):
    df = dataframe
    country_vals = {}
    result_df = df.groupby('Country')[
        'Name of institution'].nunique().reset_index()

    # Rename the columns for clarity
    result_df.columns = ['Country', 'Number of Institutions']
    # result_df = result_df.sort_values(
    #     by='Number of Institutions', ascending=True)

    result_df.index = result_df['Country']

    gData = [
        dict(
            type="scatter",
            mode="markers",
            x=result_df.index,
            y=result_df["Number of Institutions"] / 2,
            name="Number Of Institutions",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=result_df.index,
            y=result_df["Number of Institutions"],
            name="",
            width=0.4,

            # text=result_df["Number of Institutions"],

        ),
    ]

    # lDict_count = copy.deepcopy(lDict)
    lDict_count = dict(
        autosize=True,
        automargin=True,
        margin=dict(l=30, r=30, b=20, t=40),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation="v"),
        title="",
        mapbox=dict(
            # accesstoken=mapbox_access_token,
            style="light",
            center=dict(lon=-78.05, lat=42.54),
            zoom=7,
        ),
    )

    lDict_count["title"] = ""
    lDict_count["dragmode"] = "select"
    lDict_count["showlegend"] = False
    lDict_count["autosize"] = True
    lDict_count["xaxis"] = dict(tickangle=-45)
    lDict_count["margin"]["b"] = 150

    figure = dict(data=gData, layout=lDict_count)
    return figure


# --------------------SELECTING AN INSTITUTION-----------------------------------


@app.callback(
    Output("institutions_selected", "options"),
    [Input("selected-country", "value"),
     ],
)
def set_country_list(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataframe
    else:
        df = dataframe[dataframe["Country"] == country]

    institution_list = list(df["Name of institution"])
    # institution_list.append(df[df["Country"]])
    options = [{'label': institution, 'value': institution}
               for institution in institution_list]
    return options


# --------------------GET INSTITUTIONS RANKING DETAILS-----------------------------------


@app.callback(
    [Output("institutions_selected_ranking", "children"),
     Output("institutions_selected_country_ranking", "children"),],
    Input("institutions_selected", "value"),


)
def set_country_list(institution):
    if institution == "" or str(institution) == "None":
        p = ''
        j = ''
        return p, j
    else:
        df = dataframe.copy()
        df['Rank'] = df['SCORE'].rank(ascending=False, method='min')
        overall_ranking = list(
            df[df["Name of institution"] == institution]['Rank'])
        new_df = df[df["Name of institution"] == institution]
        country = list(new_df['Country'])

        dff = dataframe.copy()
        dff = dff[dff["Country"] == country[0]]
        dff['Rank'] = dff["KPMG's due diligence overall score"].rank(
            ascending=False, method='min')
        country_ranking = list(
            dff[dff["Name of institution"] == institution]['Rank'])

        return overall_ranking[0], country_ranking[0]


@app.callback(Output('comparison_figure', 'figure'),
              [
    Input('selected-institution_one', 'value'),
    Input('selected-institution_two', 'value')]

)
def update_graphs(institution_one, institution_two):

    uni_one_df = dataset[dataset["Institution Name"] == institution_one]
    uni_two_df = dataset[dataset["Institution Name"] == institution_two]

    val_1 = uni_one_df['Overall Input Score'].iloc[0]
    val_2 = uni_two_df['Overall Input Score'].iloc[0]

    val_3 = uni_one_df['Overall Output Score'].iloc[0]
    val_4 = uni_two_df['Overall Output Score'].iloc[0]

    val_5 = uni_one_df['Overall Impact Score'].iloc[0]
    val_6 = uni_two_df['Overall Impact Score'].iloc[0]

    val_7 = uni_one_df['SCORE'].iloc[0]
    val_8 = uni_two_df['SCORE'].iloc[0]

    data = pd.DataFrame({
        'Institution Name': [institution_one, institution_two, institution_one, institution_two, institution_one, institution_two,  institution_one, institution_two],
        'Variable': ['Overall Input Score', 'Overall Input Score', 'Overall Output Score', 'Overall Output Score', 'Overall Impact Score', 'Overall Impact Score', 'FINAL SCORE', 'FINAL SCORE'],
        'Value': [val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8]
    })

    fig = px.bar(data,
                 x='Institution Name',
                 y='Value',
                 color='Variable',
                 text='Value',
                 barmode='group',
                 color_discrete_map={'Overall Input Score': '#cbccce', 'SCORE': '#174B7D', 'Overall Output Score': '#FF5733', 'Overall Impact Score': '#2C8CFF'})

    fig.update_yaxes(range=[0, max(val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8) * 1.1],
                     title='Value')
    fig.update_xaxes(title='Institution Name', tickangle=0)
    fig.update_traces(texttemplate="%{y:,}")
    fig.update_layout(plot_bgcolor='#fff', paper_bgcolor='#fff', height=400)

    return fig


@app.callback(
    output=[Output("gfgp_self_assessment_score", "value"),
            Output("gfgp_assessment_level", "children"),
            Output("kpmg_due_dilligence_score", "value"),
            Output("inst_in_quest", "children"),
            Output("country_in_quest", "children"),

            ],
    inputs=Input("institutions_selected", "value"),
)
def update_gauge(institution):

    print(institution)

    if institution:
        df = dataframe[dataframe["Name of institution"] == institution]
        gfgp_self_assessment_score = df['GFGP Self-Assessment Score'].iloc[0]
        gfgp_assessment_level = df['GFGP Assessment Level'].iloc[0]
        kpmg_due_dilligence_score = df["KPMG's due diligence overall score"].iloc[0]
        detail = str('Institution: '+institution)
        county = str('Country: '+df['Country'].iloc[0])

        # overall_score = df['SCORE'].iloc[0]
        # medical_dept = df['Medical Dep'].iloc[0]
        # socialogy_dept = df['Sociology'].iloc[0]
        # agriculture_dept = df['Agri Dep'].iloc[0]
        # business_dept = df['Business/ commerce/Economics Dep'].iloc[0]
        print(gfgp_self_assessment_score, gfgp_assessment_level,
              kpmg_due_dilligence_score, detail, county)

        return gfgp_self_assessment_score, gfgp_assessment_level, kpmg_due_dilligence_score, detail, county
    else:
        return 0, '', 0, '', ''


@app.callback(
    Output("gfgp_self_assessment_score", "color"),
    Input("gfgp_self_assessment_score", "value")
)
def update_gauge_color1(value):
    if value == 1:
        return {"gradient": True, "ranges": {"green": [0, 1]}}
    elif value == 0:
        return {"gradient": True, "ranges": {"red": [0, 1]}}
    else:
        return {"gradient": True, "ranges": {"red": [0, value], "green": [value, 1]}}


@app.callback(
    Output("kpmg_due_dilligence_score", "color"),
    Input("kpmg_due_dilligence_score", "value")
)
def update_gauge_color3(value):
    if value == 1:
        return {"gradient": True, "ranges": {"green": [0, 1]}}
    elif value == 0:
        return {"gradient": True, "ranges": {"red": [0, 1]}}
    else:
        return {"gradient": True, "ranges": {"red": [0, value], "green": [value, 1]}}


@app.callback(
    Output("overall_score", "color"),
    Input("overall_score", "value")
)
def update_gauge_color4(value):
    if value == 35:
        return {"gradient": True, "ranges": {"green": [0, 35]}}
    elif value == 0:
        return {"gradient": True, "ranges": {"red": [0, 35]}}
    else:
        return {"gradient": True, "ranges": {"red": [0, value], "green": [value, 35]}}

# Medical Departments PIE CHART ***************************************************************


@app.callback(
    [Output('medical-pie-chart', 'figure'),
     Output('medical-country', 'children'),
     Output('medical-inst', 'children')],
    [Input("selected-country", "value")],
)
def medical_inst_pie(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
        country_details = "Country: All Countries"
    else:
        df = dataset[dataset["Country"] == country]
        country_details = 'Country: '+country

    g_yes = len(df[df['Medical Dep'] == 'Yes'])
    g_no = len(df[df['Medical Dep'] == 'No'])
    if g_yes > 0:
        medical_yes = round(g_yes / (g_yes + g_no) * 100, 2)
        medical_no = round(g_no / (g_yes + g_no) * 100, 2)
        labels = ['Yes: {} ({:.2f}%)'.format(g_yes, medical_yes),
                  'No: {} ({:.2f}%)'.format(g_no, medical_no)]
        values = [medical_yes, medical_no]
        colors = ['#F29300', '#D1D0D1']

        fig_pie = go.Figure(
            data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        # Set the desired font size here
        fig_pie.update_traces(textfont_size=20)
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20), height=300)
    else:

        # empty piechat
        fig_pie = go.Figure(
            data=[go.Pie(labels=[], values=[], marker=dict(colors=[]), hole=1)])
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20))

    return fig_pie, country_details


# Agricultural Departments PIE CHART ***************************************************************


@app.callback(
    [Output('agri-pie-chart', 'figure'),
     Output('agric-country', 'children'),
     Output('agric-inst', 'children')],
    [Input("selected-country", "value")],
)
def agricultural_inst_pie(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
        country_details = "Country: All Countries"
    else:
        df = dataset[dataset["Country"] == country]
        country_details = 'Country: '+country

    g_yes = len(df[df['Agri Dep'] == 'Yes'])
    g_no = len(df[df['Agri Dep'] == 'No'])
    if g_yes > 0:
        medical_yes = round(g_yes / (g_yes + g_no) * 100, 2)
        medical_no = round(g_no / (g_yes + g_no) * 100, 2)
        labels = ['Yes: {} ({:.2f}%)'.format(g_yes, medical_yes),
                  'No: {} ({:.2f}%)'.format(g_no, medical_no)]
        values = [medical_yes, medical_no]
        colors = ['#F29300', '#D1D0D1']

        fig_pie = go.Figure(
            data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        # Set the desired font size here
        fig_pie.update_traces(textfont_size=20)
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20), height=300)
    else:

        # empty piechat
        fig_pie = go.Figure(
            data=[go.Pie(labels=[], values=[], marker=dict(colors=[]), hole=1)])
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20))

    return fig_pie, country_details

# Agricultural Departments PIE CHART ***************************************************************


@app.callback(
    [Output('socialogy-pie-chart', 'figure'),
     Output('socialogy-country', 'children'),
     Output('socialogy-inst', 'children')],
    [Input("selected-country", "value"),],
)
def socialogy_inst_pie(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
        country_details = "Country: All Countries"
    else:
        df = dataset[dataset["Country"] == country]
        country_details = 'Country: '+country

    g_yes = len(df[df['Sociology'] == 'Yes'])
    g_no = len(df[df['Sociology'] == 'No'])
    if g_yes > 0:
        medical_yes = round(g_yes / (g_yes + g_no) * 100, 2)
        medical_no = round(g_no / (g_yes + g_no) * 100, 2)
        labels = ['Yes: {} ({:.2f}%)'.format(g_yes, medical_yes),
                  'No: {} ({:.2f}%)'.format(g_no, medical_no)]
        values = [medical_yes, medical_no]
        colors = ['#9A1650', '#D1D0D1']

        fig_pie = go.Figure(
            data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        # Set the desired font size here
        fig_pie.update_traces(textfont_size=20)
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20), height=300)
    else:

        # empty piechat
        fig_pie = go.Figure(
            data=[go.Pie(labels=[], values=[], marker=dict(colors=[]), hole=1)])
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20))

    return fig_pie, country_details

# Business Departments PIE CHART ***************************************************************


@app.callback(
    [Output('business-pie-chart', 'figure'),
     Output('business-country', 'children'),
     Output('business-inst', 'children')],
    [Input("selected-country", "value"),],
)
def business_inst_pie(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
        country_details = "Country: All Countries"
    else:
        df = dataset[dataset["Country"] == country]
        country_details = 'Country: '+country

    g_yes = len(df[df['Business/ commerce/Economics Dep'] == 'Yes'])
    g_no = len(df[df['Business/ commerce/Economics Dep'] == 'No'])
    if g_yes > 0:
        medical_yes = round(g_yes / (g_yes + g_no) * 100, 2)
        medical_no = round(g_no / (g_yes + g_no) * 100, 2)
        labels = ['Yes: {} ({:.2f}%)'.format(g_yes, medical_yes),
                  'No: {} ({:.2f}%)'.format(g_no, medical_no)]
        values = [medical_yes, medical_no]
        colors = ['#9A1650', '#D1D0D1']

        fig_pie = go.Figure(
            data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        # Set the desired font size here
        fig_pie.update_traces(textfont_size=20)
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=10, r=10, t=30, b=20), height=300)
    else:

        # empty piechat
        fig_pie = go.Figure(
            data=[go.Pie(labels=[], values=[], marker=dict(colors=[]), hole=1)])
        fig_pie.update_layout(title="", template='seaborn',
                              margin=dict(l=20, r=20, t=30, b=20))

    return fig_pie, country_details

# INPUT SCORE DISTRIBUTIONS


@app.callback(
    Output("input_score_normal-distribution-graph", "figure"),
    [Input("selected-country", "value"),
     ],
)
def update_graph(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    key = []
    vals = []
    for item in range(1, 11):
        val = len(df[df['Overall Input Score'] == item])
        key.append(item)
        vals.append(val)

    x = key
    y = vals

    trace = go.Bar(x=x, y=y, name="Normal Distribution",
                   marker=dict(color='#FF7F0F'))

    layout = go.Layout(
        title="Institutions Input Score Distribution",
        xaxis=dict(title="Score", type='category',
                   categoryorder='array', categoryarray=x),
        yaxis=dict(title="Distirbution Density"),
        margin=dict(l=40, r=0, t=40, b=30),
        bargap=0.1
    )

    return {"data": [trace], "layout": layout}

# OUTPUT SCORE DISTRIBUTIONS


@app.callback(
    Output("output_score_normal-distribution-graph", "figure"),
    [Input("selected-country", "value"),],
)
def update_graph(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    key = []
    vals = []
    for item in range(1, 11):
        val = len(df[df['Overall Output Score'] == item])
        key.append(item)
        vals.append(val)

    x = key
    y = vals

    trace = go.Bar(x=x, y=y, name="Normal Distribution",
                   marker=dict(color='#FF7F0F'))

    layout = go.Layout(
        title="Institutions Output Score Distribution",
        xaxis=dict(title="Score", type='category',
                   categoryorder='array', categoryarray=x),
        yaxis=dict(title="Distirbution Density"),
        margin=dict(l=40, r=0, t=40, b=30),
        bargap=0.1
    )

    return {"data": [trace], "layout": layout}

# IMPACT SCORE DISTRIBUTIONS


@app.callback(
    Output("impact_score_normal-distribution-graph", "figure"),
    [Input("selected-country", "value"),],
)
def impact_update_graph(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    key = []
    vals = []
    for item in range(1, 11):
        val = len(df[df['Overall Impact Score'] == item])
        key.append(item)
        vals.append(val)

    x = key
    y = vals

    trace = go.Bar(x=x, y=y, name="Normal Distribution",
                   marker=dict(color='#FF7F0F'))

    layout = go.Layout(
        title="Institutions Impact Score Distribution",
        xaxis=dict(title="Score", type='category',
                   categoryorder='array', categoryarray=x),
        yaxis=dict(title="Distirbution Density"),
        margin=dict(l=40, r=0, t=40, b=30),
        bargap=0.1
    )

    return {"data": [trace], "layout": layout}

# OVERALL SCORE DISTRIBUTIONS


@app.callback(
    Output("overall_score_normal-distribution-graph", "figure"),
    [Input("selected-country", "value"),],
)
def overall_update_graph(country):
    if str(country) == "All Countries" or str(country) == "None":
        df = dataset
    else:
        df = dataset[dataset["Country"] == country]

    key = []
    vals = []
    for item in range(1, 36):
        val = len(df[df['SCORE'] == item])
        key.append(item)
        vals.append(val)

    x = key
    y = vals

    trace = go.Bar(x=x, y=y, name="Normal Distribution",
                   marker=dict(color='#FF7F0F'))

    layout = go.Layout(
        title="Institutions Overall Score Distribution",
        xaxis=dict(title="Score", type='category',
                   categoryorder='array', categoryarray=x),
        yaxis=dict(title="Distirbution Density"),
        margin=dict(l=40, r=0, t=40, b=30),
        bargap=0.1
    )

    return {"data": [trace], "layout": layout}


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8041)
