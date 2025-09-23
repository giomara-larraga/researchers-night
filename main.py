"""
Phone Selection Dashboard Application

This application provides a multi-criteria decision support tool for selecting optimal phones
based on user preferences. It uses a Dash web interface with Bootstrap components to create
an interactive experience where users can specify their preferences for operating system,
memory, RAM, battery capacity, and budget, and receive recommendations based on multi-objective
optimization techniques.

Key Features:
- Interactive web interface built with Dash and Bootstrap
- Multi-criteria decision analysis using aspiration-based optimization
- Visual phone comparison with images and detailed specifications
- Alternative recommendations based on proximity to user preferences

Dependencies:
- dash: Web application framework
- dash-bootstrap-components: Bootstrap styling for Dash
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- plotly: Visualization components
"""

from http import server
from pydoc import classname
from tkinter.ttk import Style
from dash import Dash, dcc, html, Input, Output, callback

import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as ex
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from flask import Response

# Data Loading and Preprocessing
# Load the main phone dataset and details configuration
data = pd.read_csv("./data/Phones_2025.csv", header=0)
details = pd.read_csv("./data/Phone_details.csv", header=0)

# Extract column names from the first row of details file
names = details.loc[0]

# Rename columns in both datasets using the extracted names
data = data.rename(columns=names)
details = details.rename(columns=names)

# Extract maximum values for normalization (row 1 of details)
maxi = details.loc[1].astype(int)

# Extract flags for which details should be displayed on cards (row 2 of details)
details_on_card = details.loc[2].astype(int)
details_on_card = details.columns[details_on_card == 1]


# Multi-Criteria Decision Analysis Configuration
# Define optimization direction for each criterion:
# -1: maximize (higher values are better)
#  1: minimize (lower values are better)
fitness_columns = {
    "Memory": -1,  # Higher memory capacity is better
    "RAM": -1,  # Higher RAM is better
    "Battery": -1,  # Higher battery capacity is better
    "Price (Euros)": 1,  # Lower price is better
}

# Normalize fitness data using maximum values for proper comparison
fitness_data = (
    data[list(fitness_columns.keys())] * maxi[list(fitness_columns.keys())].values
)

# Application assets
PLOTLY_LOGO = "assets/logo.png"

# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Initialize Dash Application
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA],  # Use Bootstrap Litera theme
    eager_loading=True,  # Load all components immediately
    suppress_callback_exceptions=True,  # Allow callbacks for components not yet rendered
)

# Main application layout with URL routing
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


# Home Page Layout
# Landing page with introduction and call-to-action button
home_page = html.Div(
    style={"backgroundColor": "#002957"},  # Dark blue background
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

# Main Application Page Layout
# Interactive phone selection interface with preferences form and results display
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
                                                            "Choose desired Memory capacity (GB)",
                                                            html_for="memory-choice",
                                                        ),
                                                        dcc.Slider(
                                                            id="memory-choice",
                                                            min=128,
                                                            max=1024,
                                                            step=None,
                                                            included=False,
                                                            value=256,
                                                            marks={
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
                                                            min=4,
                                                            max=24,
                                                            step=None,
                                                            value=8,
                                                            included=False,
                                                            marks={
                                                                4: "4",
                                                                6: "6",
                                                                8: "8",
                                                                10: "10",
                                                                12: "12",
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
                                                            min=4000,
                                                            max=7000,
                                                            step=100,
                                                            included=False,
                                                            value=5000,
                                                            marks={
                                                                4000: "4000",
                                                                4500: "4500",
                                                                5000: "5000",
                                                                5500: "5500",
                                                                6000: "6000",
                                                                6500: "6500",
                                                                6500: "6500",
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
                                                            min=50,
                                                            max=2000,
                                                            step=50,
                                                            included=False,
                                                            value=600,
                                                            marks={
                                                                50: "50",
                                                                200: "200",
                                                                400: "400",
                                                                600: "600",
                                                                800: "800",
                                                                1000: "1000",
                                                                1200: "1200",
                                                                1400: "1400",
                                                                1600: "1600",
                                                                1800: "1800",
                                                                2000: "2000",
                                                            },
                                                            className="dash-slider",
                                                        ),
                                                    ],
                                                    className="mr-3 ml-3 mb-4 mt-4",
                                                    style={
                                                        "position": "relative",
                                                        "zIndex": "1000",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "maxHeight": "600px",
                                                "overflow": "visible",
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


# Main Callback Function for Phone Recommendation
@callback(
    [
        Output("results", "children"),  # Best phone details table
        *[Output(f"figure-result", "children")],  # Best phone image
        *[
            Output(f"figure-option-{i}", "children") for i in range(2, 6)
        ],  # Alternative phone images
        *[
            Output(f"other-results-list-{i}", "children") for i in range(2, 6)
        ],  # Alternative phone names
        *[
            Output(f"other-results-tooltip-{i}", "children") for i in range(2, 6)
        ],  # Alternative phone tooltips
    ],
    [
        Input(f"{attr}-choice", "value")
        for attr in ["memory", "ram", "cam", "cost"]  # User preference inputs
    ],
)
def results(*choices):
    """
    Calculate optimal phone recommendations based on user preferences.

    Uses aspiration-based multi-criteria decision analysis to find phones that best
    match user preferences. The algorithm:
    1. Normalizes all criteria to a common scale
    2. Calculates ideal and nadir points
    3. Measures distance from user aspirations to each phone
    4. Ranks phones by minimum distance (closest match)

    Args:
        *choices: Tuple containing user preferences for:
            - Desired memory capacity (GB)
            - Desired RAM capacity (GB)
            - Desired battery capacity (mAh)
            - Budget constraint (Euros)

    Returns:
        Tuple containing:
        - Best phone details table
        - Best phone image
        - Alternative phone images (up to 4)
        - Alternative phone names (up to 4)
        - Alternative phone detail tooltips (up to 4)
    """
    # Use all available phone data (OS filter removed)
    choice_data = data

    # Extract relevant criteria for optimization
    # These criteria have different units: Memory(GB), RAM(GB), Battery(mAh), Price(€)
    # Proper normalization is essential for meaningful comparison
    relevant_data = choice_data[
        [
            "Memory",
            "RAM",
            "Battery",
            "Price (Euros)",
        ]
    ].reset_index(drop=True)
    # Prepare data for display cards (include Id for image mapping)
    card_data_columns = list(details_on_card) + ["Id"]
    card_data = choice_data[card_data_columns].reset_index(drop=True)

    # NORMALIZATION STRATEGY:
    # Problem: Criteria have different units and scales (GB vs mAh vs €)
    # Solution: Normalize both data and aspirations to [0,1] scale before distance calculation
    # This ensures all criteria contribute equally to the final ranking

    # Step 1: Normalize data to [0,1] scale for each criterion
    # This handles different units (GB, mAh, €) by scaling to common range
    data_min = relevant_data.min().values
    data_max = relevant_data.max().values
    data_range = data_max - data_min

    # Normalize data to [0,1] where 0 = worst value, 1 = best value for each criterion
    normalized_data = (relevant_data - data_min) / data_range

    # Step 2: Apply optimization directions AFTER normalization
    # For minimize criteria (Price), flip the scale: 1-normalized_value
    # For maximize criteria (Memory, RAM, Battery), keep as is
    optimization_directions = np.array([1, 1, 1, -1])  # 1=maximize, -1=minimize

    for i, direction in enumerate(optimization_directions):
        if direction == -1:  # Minimize criterion (Price)
            normalized_data.iloc[:, i] = 1 - normalized_data.iloc[:, i]

    # Step 3: Normalize user aspirations to the same [0,1] scale
    aspirations = np.array(choices)  # All choices are now numerical preferences
    normalized_aspirations = (aspirations - data_min) / data_range

    # Apply same optimization direction transformation to aspirations
    for i, direction in enumerate(optimization_directions):
        if direction == -1:  # Minimize criterion (Price)
            normalized_aspirations[i] = 1 - normalized_aspirations[i]

    # Step 4: Calculate distance in normalized space
    # Uses Chebyshev distance (maximum deviation across all criteria)
    # Now both data and aspirations are in [0,1] scale, so distances are meaningful
    distance = np.abs(normalized_aspirations - normalized_data).max(axis=1)

    # Sort phones by distance (smallest distance = best match)
    distance_order = np.argsort(distance)
    # Generate results for the best matching phone
    best = table_from_data(card_data.loc[distance_order.values[0]], choices)

    # Generate alternative options (up to 4 additional phones)
    total_number = len(distance_order)
    if total_number >= 4:
        # If enough phones available, show next 4 best options
        others, tooltips, figures = other_options(
            card_data.loc[distance_order.values[1:5]]
        )
    else:
        # If fewer phones available, show all remaining and pad with empty slots
        others, tooltips, figures = other_options(
            card_data.loc[distance_order.values[1:total_number]]
        )
        others = others + [f"{i}. -" for i in range(len(others) + 2, 6)]
        tooltips = tooltips + [None for i in range(len(tooltips) + 2, 6)]
        figures = figures + [None for i in range(len(figures) + 2, 6)]

    # Generate image component for the best phone
    id = card_data.loc[distance_order.values[0]]["Id"]
    print(f"DEBUG: Best phone ID = {id}")  # Debug output
    import time

    idresult = html.Div(
        html.Img(
            src=app.get_asset_url(f"images/{id}.jpg"),
            style={"width": "70%"},
        )
    )

    return (best, idresult, *figures, *others, *tooltips)


def table_from_data(data, choices):
    """
    Create a formatted table showing phone specifications with color-coded comparison to user preferences.

    Args:
        data: Pandas Series containing phone specifications
        choices: List of user preference values [memory, ram, battery, price]

    Returns:
        dbc.Table: Bootstrap table component with specifications and color indicators
    """
    # Criteria that can be compared to user preferences
    comparable_criteria = ["Memory", "RAM", "Battery", "Price (Euros)"]

    # Calculate difference between phone specs and user preferences
    # For Memory, RAM, Battery: phone_value - user_preference (positive = phone exceeds preference)
    # For Price: (phone_value - user_preference) * -1 (positive = phone is cheaper than budget)
    diff = (data[comparable_criteria].values - choices) * [1, 1, 1, -1]

    # Create color mapping for comparable criteria
    color_map = {}
    for i, col in enumerate(comparable_criteria):
        # GREEN = phone meets or exceeds preference (higher Memory/RAM/Battery, or lower Price)
        # RED = phone falls short of preference (lower Memory/RAM/Battery, or higher Price)
        color_map[col] = "green" if diff[i] >= 0 else "red"

    # Create table rows for all displayed specifications
    table_rows = []
    # Skip the first column (usually Model name) and show the rest
    for col in data.index[1:]:
        if col in comparable_criteria:
            # Show color indicator for comparable criteria
            color_indicator = html.Span(" ▉", style={"color": color_map[col]})
        else:
            # No color indicator for non-comparable criteria
            color_indicator = html.Span(" ", style={"color": "transparent"})

        table_rows.append(
            html.Tr(
                [
                    html.Th(col),  # Specification name
                    html.Td([str(data[col])]),  # Actual value
                    html.Td([color_indicator]),  # Color indicator (or empty)
                ]
            )
        )

    return dbc.Table([html.Tbody(table_rows)])


def table_from_data_horizontal(data):
    """
    Create a horizontal table layout for displaying phone specifications in tooltips.

    Args:
        data: Pandas Series containing phone specifications

    Returns:
        dbc.Table: Bootstrap table with horizontal layout (columns = specifications)
    """
    header = [html.Thead(html.Tr([html.Th(col) for col in data.index]))]
    body = [html.Tbody([html.Tr([html.Td(data[col]) for col in data.index])])]
    return dbc.Table(header + body)


def get_figures_options(id):
    """
    Create an image component for alternative phone options.

    Args:
        id: Phone ID used to locate the corresponding image file

    Returns:
        html.Div: Div containing the phone image
    """
    import time

    cache_bust = int(time.time())  # Current timestamp to prevent caching
    return html.Div(
        html.Img(
            src=app.get_asset_url(f"images/{id}.jpg?v={cache_bust}"),
            style={"width": "70%"},
        )
    )


def other_options(data):
    """
    Process alternative phone options to generate display components.

    Args:
        data: DataFrame containing alternative phone specifications

    Returns:
        tuple: (contents, tables, figures)
            - contents: List of phone names with numbering
            - tables: List of specification tables for tooltips
            - figures: List of phone images
    """
    contents = []  # Phone names for display
    tables = []  # Specification tables for tooltips
    figures = []  # Phone images
    i = 2  # Start numbering from 2 (since 1 is the best phone)

    for index, row in data.iterrows():
        contents.append(f"{i}. {row['Model']}")
        id = row["Id"]
        tables.append(
            table_from_data_horizontal(row[1:])
        )  # Skip first column (Model name)
        figures.append(get_figures_options(id))
        i = i + 1

    return contents, tables, figures


# URL Routing Callback
@callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    """
    Handle URL routing to display appropriate page content.

    Args:
        pathname: URL pathname from browser

    Returns:
        html.Div: Page content corresponding to the requested URL
    """
    if pathname == "/home":
        return home_page
    elif pathname == "/app":
        return app_page
    else:
        return home_page  # Default to home page for unrecognized URLs


# Application Entry Point
if __name__ == "__main__":
    """
    Run the Dash application server.

    The application will be available at http://127.0.0.1:8050/
    Debug mode is enabled for development purposes.
    """
    app.run_server(debug=True)
