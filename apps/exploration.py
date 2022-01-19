import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.express as px
import plotly.graph_objects as go
from plotly.tools import mpl_to_plotly
import json
import numpy as np
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #css style template

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
# dfa.columns = dfa.columns.str.title()
uk_cities = json.load(open("data/uk_districts.geojson", "r"))
dfa = dfa.dropna()

road_guide = pd.read_excel('data/Road-Safety-Open-Dataset-Data-Guide.xlsx')
district_names = road_guide[road_guide['field name'] == 'local_authority_district']
district_names.rename(columns={"code/format" :"local_authority_district"}, inplace=True)
dfa['local_authority_district'] = dfa['local_authority_district'].map(district_names.set_index('local_authority_district')['label'])

df1 = dfa[['local_authority_ons_district', 'number_of_casualties', 'accident_year']]
df1['number_of_accidents'] = 1
district_names = road_guide[road_guide['field name'] == 'local_authority_ons_district']
district_names.rename(columns={"code/format": "local_authority_ons_district"}, inplace=True)
ons_names = district_names[['local_authority_ons_district', 'label']]
df_final = pd.merge(df1, ons_names, on="local_authority_ons_district", how="left")
years = dfa['accident_year'].unique()
cities = df_final['label'].dropna().unique()



layout = html.Div([
    html.Div([
        dcc.Graph(id='choropleth-map', style={'width': '60%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='accident-graph', style={'width': '40%', 'float': 'right'}, figure={}, clickData=None),
        ]),
    html.Div([
        # dcc.Graph(id='choropleth-map1', style={'width': '60%', 'float': 'left'}, figure=fig1),
    ]),
    html.Div([
        html. Label("choose a city"),
            dcc.Dropdown(
                id = 'city',
                options = [
                    {"label": i , "value" : i } for i in cities],
            placeholder= 'select a city'),
        ]),
    html.Div([
    html. Label("choose a year range"),
        dcc.RangeSlider(
                    id = "year",
                    min = 2016,
                    max = 2020,
                    value = [2016, 2020],
                    marks = { str(i): str(i)  for i in years },
                )
        ],style={"width": "70%", "position":"absolute",
                 "left":"5%"})
])

    
