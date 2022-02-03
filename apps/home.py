from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import json

# needed only if running this as a single page app
#external_stylesheets = [dbc.themes.LUX]

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# change to app.layout if running as single page app instead
dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
dfc = pd.read_csv('data/dft-road-casualty-statistics-casualty-last-5-years.csv')
dfv = pd.read_csv('data/dft-road-casualty-statistics-vehicle-last-5-years.csv')
road_guide = pd.read_excel('data/Road-Safety-Open-Dataset-Data-Guide.xlsx')
uk_cities = json.load(open("data/uk_districts.geojson", "r"))

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Welcome to the Hawkeye Visualization tool of Group 45", className="text-center")
                    , className="mb-5 mt-5")
        ]),
        dbc.Row([
            dbc.Col(html.H5(children='A dataset about the Road accidents in UK in last 5 years has been analysed in this web tool. The link for the dataset you can find below.'
                                     )
                    , className="mb-4")
            ]),

        dbc.Row([
            dbc.Col(html.H5(children='The tool consists of two main pages: Home tab, '
                                     'this is an introduction page to the Group 45 visualization tool. '
                                     'Exploration tab, which gives the oppurtunity to explore the dataset and '
                                     'find interesting patterns')
                    , className="mb-5")
        ]),

        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Get the original datasets used in this project',
                                               className="text-center"),
                                       dbc.Button("UK-Road-Safety",
                                                  href="https://data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data",
                                                  color="primary",
                                                  target="_blank",
                                                  className="mt-3")
                                       ],
                             body=True, color="dark", outline=True)
                    , width=6, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='You can find the code for this project in',
                                               className="text-center"),
                                       dbc.Button("GitHub",
                                                  href="https://github.com/nikhil-96/Hawkeye_Viz",
                                                  color="primary",
                                                  target="_blank",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True)
                    , width=6, className="mb-4")
        ], className="mb-5")

    ])

])
