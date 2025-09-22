from http import server
from pydoc import classname
from tkinter.ttk import Style
from dash import Dash, dcc, html, Input, Output, callback

# from dash.exceptions import PreventUpdate
# from dash import dcc
# from dash import html

# from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as ex
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from flask import Response

data = pd.read_csv("./data/Phones_2025.csv", header=0)
details = pd.read_csv("./data/Phone_details.csv", header=0)

names = details.loc[0]

data = data.rename(columns=names)

details = details.rename(columns=names)

maxi = details.loc[1].astype(int)
details_on_card = details.loc[2].astype(int)

details_on_card = details.columns[details_on_card == 1]


fitness_columns = {
    "Memory": -1,
    "RAM": -1,
    "Battery": -1,
    "Price (Euros)": 1,
}

fitness_data = (
    data[list(fitness_columns.keys())] * maxi[list(fitness_columns.keys())].values
)
PLOTLY_LOGO = "assets/logo.png"

# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA],
    eager_loading=True,
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


home_page = html.Div(
    style={"backgroundColor": "#002957"},
    children=[
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    children=[
                                        html.H1(
                                            children="Find your optimal phone",
                                            className="main-title",
                                        ),
                                        html.P(
                                            (
                                                "This app uses decision support tools to "
                                                "quickly and easily find phones which reflect "
                                                "the user's desires. You only need to input your preferences "
                                                "and the app will show you the phone "
                                                "which matches the preferences the best. "
                                                "In case you do not like the suggested phone,"
                                                "the app also shows you some alternatives close to your preferences."
                                            ),
                                            className="main-p",
                                        ),
                                        html.Div(
                                            children=[
                                                dcc.Link(
                                                    dbc.Button(
                                                        "START",
                                                        color="primary",
                                                        className="start-button",
                                                    ),
                                                    href="/app",
                                                    refresh=True,
                                                ),
                                                # dbc.Button("START", color="primary", className="start-button")
                                            ],
                                            className="start-button-div",
                                        ),
                                    ],
                                    width=6,
                                    className="main-col-text",
                                ),
                                dbc.Col(
                                    children=[
                                        # html.P("Example")
                                        html.Img(
                                            src=r"assets/home_screen.png",
                                            alt="image",
                                            className="main_figure",
                                        )
                                    ],
                                    width=6,
                                    className="figure-main",
                                ),
                            ],
                            className="row-main",
                        )
                    ]
                )
            ],
            className="g-0 row-main",
        ),
    ],
)

app_page = html.Div(
    children=[
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                                dbc.Col(
                                    dbc.NavbarBrand(
                                        "Multiobjective Optimization Group - Phone selection tool",
                                        className="ms-2",
                                    )
                                ),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                ]
            ),
            color="#002957",
            dark=True,
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        # Top card with details(?)
                        dbc.Card(
                            children=[
                                dbc.CardHeader("Your preferences"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            (
                                                "INSTRUCTIONS: Input your preferences "
                                                "below. The box on top right shows the phone "
                                                "which matches the preferences the best. "
                                                "The box on bottom right provides some "
                                                "close alternatives."
                                            ),
                                            className="card-text",
                                        ),
                                        dbc.Form(
                                            [
                                                dbc.Row(
                                                    children=[
                                                        dbc.Label(
                                                            "Choose desired operating system",
                                                            html_for="os-choice",
                                                        ),
                                                        dbc.RadioItems(
                                                            options=[
                                                                {
                                                                    "label": "Android",
                                                                    "value": "Android",
                                                                },
                                                                {
                                                                    "label": "iOS",
                                                                    "value": "IOS",
                                                                },
                                                                {
                                                                    "label": "No preference",
                                                                    "value": "both",
                                                                },
                                                            ],
                                                            id="os-choice",
                                                            value="both",
                                                            inline=True,
                                                            # className="text-center mt-4",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-2 mt-2",
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Label(
                                                            "Choose desired Memory capacity (GB)",
                                                            html_for="memory-choice",
                                                        ),
                                                        dcc.Slider(
                                                            id="memory-choice",
                                                            min=64,
                                                            max=1024,
                                                            step=None,
                                                            included=False,
                                                            value=256,
                                                            marks={
                                                                64: "64",
                                                                128: "128",
                                                                256: "256",
                                                                512: "512",
                                                                1024: "1024",
                                                            },
                                                            className="dash-slider",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-4 mt-4",
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Label(
                                                            "Choose desired RAM capacity (GB)",
                                                            html_for="ram-choice",
                                                        ),
                                                        dcc.Slider(
                                                            id="ram-choice",
                                                            min=2,
                                                            max=12,
                                                            step=1,
                                                            value=12,
                                                            included=False,
                                                            marks={
                                                                4: "4",
                                                                6: "6",
                                                                8: "8",
                                                                12: "12",
                                                                16: "16",
                                                                24: "24",
                                                            },
                                                            className="dash-slider",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-4 mt-4",
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Label(
                                                            "Choose desired battery capacity (1000mAh)",
                                                            html_for="cam-choice",
                                                        ),
                                                        dcc.Slider(
                                                            id="cam-choice",
                                                            min=4200,
                                                            max=7000,
                                                            step=200,
                                                            included=False,
                                                            value=70,
                                                            marks={
                                                                4200: "4200",
                                                                4500: "4500",
                                                                5000: "5000",
                                                                5200: "5200",
                                                                5400: "5400",
                                                                5500: "5500",
                                                                5820: "5820",
                                                                6000: "6000",
                                                                6300: "6300",
                                                                7000: "7000",
                                                            },
                                                            className="dash-slider",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-2 mt-3",
                                                ),
                                                dbc.Row(
                                                    children=[
                                                        dbc.Label(
                                                            "Choose desired budget (Euros)",
                                                            html_for="cost-choice",
                                                        ),
                                                        dcc.Slider(
                                                            id="cost-choice",
                                                            min=200,
                                                            max=1200,
                                                            step=1,
                                                            included=False,
                                                            value=100,
                                                            marks={
                                                                50: "50",
                                                                100: "100",
                                                                600: "600",
                                                                800: "800",
                                                                1000: "1000",
                                                                1200: "1200",
                                                            },
                                                            className="dash-slider",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-4 mt-4",
                                                ),
                                            ],
                                            style={
                                                "maxHeight": "560px",
                                                "overflow": "hidden",
                                            },
                                            className="form_preferences",
                                        ),
                                    ]
                                ),
                            ],
                            className="mr-3 ml-3 mb-2 mt-2",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    children=[
                        dbc.Card(
                            children=[
                                dbc.CardHeader("The best phone for you is:"),
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            children=[
                                                # html.Div(html.Img(src=app.get_asset_url('images/1.jpg'), style={'width':'70%'}))
                                                html.Div(
                                                    id="figure-result",
                                                    style={
                                                        "align-items": "center",
                                                        "padding": "1em",
                                                    },
                                                )
                                            ],
                                            width=4,
                                        ),
                                        dbc.Col(
                                            children=[
                                                dbc.CardBody(
                                                    id="results",
                                                    children=[],
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            children=[
                                dbc.CardHeader("Other great phones:"),
                                dbc.CardBody(
                                    id="other-results",
                                    children=(
                                        [
                                            dbc.Row(
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            dbc.Row(
                                                                html.Div(
                                                                    id=f"figure-option-{i}"
                                                                )
                                                            ),
                                                            dbc.Row(
                                                                html.Span(
                                                                    f"{i}. ",
                                                                    id=f"other-results-list-{i}",
                                                                )
                                                            ),
                                                        ]
                                                    )
                                                    for i in range(2, 6)
                                                ]
                                            ),
                                        ]
                                        + [
                                            dbc.Tooltip(
                                                id=f"other-results-tooltip-{i}",
                                                target=f"figure-option-{i}",
                                                placement="bottom",
                                                className="tooltip-details",
                                            )
                                            for i in range(2, 6)
                                        ]
                                    ),
                                ),
                            ],
                            className="mt-4",
                        ),
                        html.Div(id="tooltips"),
                    ],
                    width=6,
                    className="mb-2 mt-2",
                ),
            ],
            className="row-main-content",
        ),
        dbc.Row([html.Div(id="callback-dump")]),
    ],
    className="div_app",
)


@callback(
    [
        Output("results", "children"),
        *[Output(f"figure-result", "children")],
        *[Output(f"figure-option-{i}", "children") for i in range(2, 6)],
        *[Output(f"other-results-list-{i}", "children") for i in range(2, 6)],
        *[Output(f"other-results-tooltip-{i}", "children") for i in range(2, 6)],
    ],
    [
        Input(f"{attr}-choice", "value")
        for attr in ["os", "memory", "ram", "cam", "cost"]
    ],
)
def results(*choices):
    choice_data = data
    """     
    if choices[0] == "both":
        choice_data = data
    elif choices[0] == "IOS":
        choice_data = data[[True if "iOS" in st else False for st in data["OS"]]]
    if choices[0] == "Android":
        choice_data = data[[True if "Android" in st else False for st in data["OS"]]] """
    relevant_data = choice_data[
        [
            "Memory",
            "RAM",
            "Battery",
            "Price (Euros)",
        ]
    ].reset_index(drop=True)
    # Include 'Id' column in card_data for the other_options function
    card_data_columns = list(details_on_card) + ["Id"]
    card_data = choice_data[card_data_columns].reset_index(drop=True)
    maxi = np.asarray([-1, -1, -1, 1])
    relevant_data = relevant_data * maxi
    ideal = relevant_data.min().values
    nadir = relevant_data.max().values
    aspirations = choices[1:] * maxi
    distance = (aspirations - relevant_data) / (ideal - nadir)
    distance = distance.max(axis=1)
    distance_order = np.argsort(distance)
    best = table_from_data(card_data.loc[distance_order.values[0]], choices[1:])
    total_number = len(distance_order)
    if total_number >= 4:
        others, tooltips, figures = other_options(
            card_data.loc[distance_order.values[1:5]]
        )
    else:
        others, tooltips, figures = other_options(
            card_data.loc[distance_order.values[1:total_number]]
        )
        others = others + [f"{i}. -" for i in range(len(others) + 2, 6)]
        tooltips = tooltips + [None for i in range(len(tooltips) + 2, 6)]
        figures = figures + [None for i in range(len(figures) + 2, 6)]
    id = card_data.loc[distance_order.values[0]]["Id"]
    idresult = html.Div(
        html.Img(src=app.get_asset_url(f"images/{id}.jpg"), style={"width": "70%"})
    )

    # idoptions = html.Div(html.Img(src=app.get_asset_url(f"images/{i}.jpg" for i in range(2,6)), style={'width':'70%'}))
    return (best, idresult, *figures, *others, *tooltips)


def table_from_data(data, choices):
    # print(choices)
    to_compare = ["Memory", "RAM", "Battery", "Price (Euros)"]
    # print(data[to_compare].values)
    # print(data)

    diff = (data[to_compare].values - choices) * [1, 1, 1, -1]
    colors = [None, None, None] + ["green" if x >= 0 else "red" for x in diff]
    # print(np.sign(diff))
    return dbc.Table(
        [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Th(col),
                            html.Td(
                                [
                                    str(data[col]),
                                ],
                            ),
                            html.Td(
                                [
                                    html.Span(
                                        " ▉",
                                        style={
                                            "color": c,
                                        },
                                    )
                                ],
                            ),
                        ]
                    )
                    for (col, c) in zip(data.index[1:], colors)
                ]
            )
        ]
    )


def table_from_data_horizontal(data):
    header = [html.Thead(html.Tr([html.Th(col) for col in data.index]))]
    body = [html.Tbody([html.Tr([html.Td(data[col]) for col in data.index])])]
    return dbc.Table(header + body)


def get_figures_options(id):
    return html.Div(
        html.Img(src=app.get_asset_url(f"images/{id}.jpg"), style={"width": "70%"})
    )


def other_options(data):
    contents = []
    tables = []
    figures = []
    i = 2
    for index, row in data.iterrows():
        contents.append(f"{i}. {row['Model']}")
        id = row["Id"]
        tables.append(table_from_data_horizontal(row[1:]))
        figures.append(get_figures_options(id))
        i = i + 1
    return contents, tables, figures


@callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/home":
        return home_page
    elif pathname == "/app":
        return app_page
    else:
        return home_page
    # You could also return a 404 "URL not found" page here


if __name__ == "__main__":
    app.run_server(debug=True)
