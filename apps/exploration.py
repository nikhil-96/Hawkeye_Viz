import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.express as px
import plotly.graph_objects as go
from plotly.tools import mpl_to_plotly
import numpy as np
import pandas as pd
from apps.home import dfa, dfc, dfv, road_guide

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #css style template

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# dfa.columns = dfa.columns.str.title()

dfa.dropna(inplace=True)
dfc.dropna(inplace=True)
dfv.dropna(inplace=True)

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
district_names = road_guide[road_guide['field name'] == 'casualty_class']
district_names.rename(columns={"code/format": "casualty_class"}, inplace=True)
acc_cas_veh_df['casualty_class'] = acc_cas_veh_df['casualty_class'].map(district_names.set_index('casualty_class')['label'])
district_names = road_guide[road_guide['field name'] == 'sex_of_casualty']
district_names.rename(columns={"code/format": "sex_of_casualty"}, inplace=True)
acc_cas_veh_df['sex_of_casualty'] = acc_cas_veh_df['sex_of_casualty'].map(district_names.set_index('sex_of_casualty')['label'])
cas_sev = acc_cas_veh_df.groupby(['casualty_severity'])['accident_index'].count().rename('Total Number of Accidents').to_frame()

district_names = road_guide[road_guide['field name'] == 'urban_or_rural_area']
district_names.rename(columns={"code/format": "urban_or_rural_area"}, inplace=True)
acc_cas_veh_df.drop(acc_cas_veh_df.loc[acc_cas_veh_df['urban_or_rural_area'] == 3].index, inplace=True)
acc_cas_veh_df.drop(acc_cas_veh_df.loc[acc_cas_veh_df['urban_or_rural_area'] == -1].index, inplace=True)
acc_cas_veh_df['urban_or_rural_area'] = acc_cas_veh_df['urban_or_rural_area'].map(
    district_names.set_index('urban_or_rural_area')['label'])
district_names = road_guide[road_guide['field name'] == 'road_surface_conditions']
district_names.rename(columns={"code/format": "road_surface_conditions"}, inplace=True)
acc_cas_veh_df.drop(acc_cas_veh_df.loc[acc_cas_veh_df['road_surface_conditions'] == -1].index, inplace=True)
acc_cas_veh_df['road_surface_conditions'] = acc_cas_veh_df['road_surface_conditions'].map(
    district_names.set_index('road_surface_conditions')['label'])
district_names = road_guide[road_guide['field name'] == 'weather_conditions']
district_names.rename(columns={"code/format": "weather_conditions"}, inplace=True)
acc_cas_veh_df.drop(acc_cas_veh_df.loc[acc_cas_veh_df['weather_conditions'] == -1].index, inplace=True)
acc_cas_veh_df['weather_conditions'] = acc_cas_veh_df['weather_conditions'].map(
    district_names.set_index('weather_conditions')['label'])
district_names = road_guide[road_guide['field name'] == 'light_conditions']
district_names.rename(columns={"code/format": "light_conditions"}, inplace=True)
acc_cas_veh_df.drop(acc_cas_veh_df.loc[acc_cas_veh_df['light_conditions'] == -1].index, inplace=True)
acc_cas_veh_df['light_conditions'] = acc_cas_veh_df['light_conditions'].map(
    district_names.set_index('light_conditions')['label'])

print("Exploration")
layout = html.Div([
    html.Div([
    html.Div([
        html.Label("Choose a City", style={ 'color': 'white'}),
        dcc.Dropdown(
            id='city',
            options=[
                {"label": i, "value": i} for i in cities],
            placeholder='Select a City'),
    ], style={'color': 'black', 'width': '50%', 'padding-left':'10%', 'padding-right':'10%'}),
    html.Div([
        html.Label("Choose a Year range"),
        dcc.RangeSlider(
            id="year",
            min=2016,
            max=2020,
            value=[2016, 2020],
            marks={str(i): {'label': str(i), 'style': {'color': 'white'}} for i in years},
        )
    ], style={"width": "50%", 'float': 'left', 'color': 'white', 'padding-left':'10%', 'padding-right':'10%'})
    ], style=dict(display='flex')),
    html.Div([
        dcc.Graph(id='choropleth-map', style={'width': '60%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='severity-graph', style={'width': '40%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='days-hours-graph', style={'width': '50%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='acc-cas-graph', style={'width': '50%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='treemap-graph', style={'width': '50%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='road-speed-graph', style={'width': '50%', 'float': 'right'}, figure={}, clickData=None),
        dcc.Graph(id='violin-graph', style={'width': '50%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='factors-graph', style={'width': '50%', 'float': 'right'}, figure={}, clickData=None)
    ])
])
