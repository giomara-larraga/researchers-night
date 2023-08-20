from pydoc import classname
from dash import Dash, dcc, html
#from dash.exceptions import PreventUpdate
#from dash import dcc
#from dash import html

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as ex
import plotly.graph_objects as go
import pandas as pd
import numpy as np


data = pd.read_csv("./data/Phone_dataset_new.csv", header=0)
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
    "Camera (MP)": -1,
    "Price (Euros)": 1,
}

fitness_data = data[fitness_columns] * maxi[fitness_columns].values


#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA],
    eager_loading=True,
    suppress_callback_exceptions=True,
)


app.layout = html.Div(
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
                                                dcc.Link(html.Button("START", className="start-button"), href="/app", refresh=True),
                                                dbc.Button("START", color="primary", className="start-button")
                                            ],
                                            className="start-button-div",
                                        )

                                    ],
                                    width=6,
                                    className="main-col-text",
                                ),
                                dbc.Col(
                                    children=[
                                        html.P("Example")
                                        #html.Img(src=r'assets/main.jpg', alt='image')
                                    ],
                                    width=6,
                                    className="figure-main",
                                ),
                            ],
                            className="row-main"
                        )
                    ]
                )
            ],
            className="g-0 row-main",
        ),
        
    ],
)


@app.callback(
    [
        Output("results", "children"),
        *[Output(f"other-results-list-{i}", "children") for i in range(2, 6)],
        *[Output(f"other-results-tooltip-{i}", "children") for i in range(2, 6)],
    ],
    [
        Input(f"{attr}-choice", "value")
        for attr in ["os", "memory", "ram", "cam", "cost"]
    ],
)
def results(*choices):
    if choices[0] == "both":
        choice_data = data
    elif choices[0] == "IOS":
        choice_data = data[[True if "IOS" in st else False for st in data["OS"]]]
    if choices[0] == "Android":
        choice_data = data[[True if "Android" in st else False for st in data["OS"]]]
    relevant_data = choice_data[
        ["Memory", "RAM", "Camera (MP)", "Price (Euros)",]
    ].reset_index(drop=True)
    card_data = choice_data[details_on_card].reset_index(drop=True)
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
        others, tooltips = other_options(card_data.loc[distance_order.values[1:5]])
    else:
        others, tooltips = other_options(
            card_data.loc[distance_order.values[1:total_number]]
        )
        others = others + [f"{i}. -" for i in range(len(others) + 2, 6)]
        tooltips = tooltips + [None for i in range(len(tooltips) + 2, 6)]
    return (best, *others, *tooltips)


"""@app.callback(Output("tooltips", "children"), [Input("callback-dump", "children")])
def tooltips(tooldict):
    num = len(tooldict["ids"])
    content = []
    for i in range(num):
        content.append(dbc.Tooltip(tooldict["tables"][i], target=tooldict["ids"][i]))
    return content"""


def table_from_data(data, choices):
    # print(choices)
    to_compare = ["Memory", "RAM", "Camera (MP)", "Price (Euros)"]
    # print(data[to_compare].values)
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
                            html.Td([str(data[col]),],),
                            html.Td([html.Span(" ▉", style={"color": c,},)],),
                        ]
                    )
                    for (col, c) in zip(data.index, colors)
                ]
            )
        ]
    )


def table_from_data_horizontal(data):
    header = [html.Thead(html.Tr([html.Th(col) for col in data.index]))]
    body = [html.Tbody([html.Tr([html.Td(data[col]) for col in data.index])])]
    return dbc.Table(header + body)


def other_options(data):
    contents = []
    tables = []
    ids = []
    i = 2
    for index, row in data.iterrows():
        contents.append(f"{i}. {row['Model']}")
        tables.append(table_from_data_horizontal(row))
        i = i + 1
    return contents, tables


if __name__ == "__main__":
    app.run_server(debug=False)
