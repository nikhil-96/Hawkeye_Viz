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

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
dfc = pd.read_csv('data/dft-road-casualty-statistics-casualty-last-5-years.csv')
dfv = pd.read_csv('data/dft-road-casualty-statistics-vehicle-last-5-years.csv')

# dfa.columns = dfa.columns.str.title()
uk_cities = json.load(open("data/uk_districts.geojson", "r"))
dfa.dropna(inplace=True)
dfc.dropna(inplace=True)
dfv.dropna(inplace=True)

road_guide = pd.read_excel('data/Road-Safety-Open-Dataset-Data-Guide.xlsx')
district_names = road_guide[road_guide['field name'] == 'local_authority_district']
district_names.rename(columns={"code/format":"local_authority_district"}, inplace=True)
dfa['local_authority_district'] = dfa['local_authority_district'].map(district_names.set_index('local_authority_district')['label'])
road_names = road_guide[road_guide['field name'] == 'road_type']
road_names.rename(columns={"code/format":"road_type"}, inplace=True)
dfa['road_type'] = dfa['road_type'].map(road_names.set_index('road_type')['label'])

df1 = dfa
df1['number_of_accidents'] = 1
district_names = road_guide[road_guide['field name'] == 'local_authority_ons_district']
district_names.rename(columns={"code/format": "local_authority_ons_district"}, inplace=True)
ons_names = district_names[['local_authority_ons_district', 'label']]
df_final = pd.merge(df1, ons_names, on="local_authority_ons_district", how="left")
years = dfa['accident_year'].unique()
cities = df_final['label'].dropna().unique()

#merge datasets of accidents-casualties-vehicles
casualty_vehicle_df = dfc.merge(dfv, on=['accident_index','vehicle_reference','accident_year','accident_reference'],how='inner')

acc_cas_veh_df = casualty_vehicle_df.merge(dfa, on=['accident_index','accident_year','accident_reference'],how='inner')

cas_sev_names = road_guide[road_guide['field name'] == 'casualty_severity']
cas_sev_names.rename(columns={"code/format":"casualty_severity"}, inplace=True)
acc_cas_veh_df['casualty_severity'] = acc_cas_veh_df['casualty_severity'].map(cas_sev_names.set_index('casualty_severity')['label'])

print("Exploration")
layout = html.Div([
    html.Div([
        html.Label("Choose a City", style={ 'color': 'white'}),
        dcc.Dropdown(
            id='city',
            options=[
                {"label": i, "value": i} for i in cities],
            placeholder='Select a City'),
    ], style={'color': 'black', 'width': '100%', 'padding-left':'20%', 'padding-right':'20%'}),
    html.Div([
        dcc.Graph(id='choropleth-map', style={'width': '60%', 'float': 'left'}, figure={}, clickData=None),
        #dcc.Graph(id='accident-graph', style={'width': '40%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='acc-cas-graph', style={'width': '40%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='days-hours-graph', style={'width': '50%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='severity-graph', style={'width': '50%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='treemap-graph', style={'width': '50%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='road-speed-graph', style={'width': '50%', 'float': 'right'}, figure={}, clickData=None)

    ]),
    html.Div([
        html.Label("Choose a Year range"),
        dcc.RangeSlider(
            id="year",
            min=2016,
            max=2020,
            value=[2016, 2020],
            marks={str(i): {'label': str(i), 'style': {'color': 'white'}} for i in years},
        )
    ], style={"width": "100%", 'float': 'left', 'color': 'white', 'padding-left':'20%', 'padding-right':'20%'})
])
