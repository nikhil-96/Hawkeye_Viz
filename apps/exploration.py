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


layout = html.Div([
    html.Div([
        dcc.Graph(id='choropleth-map', style={'width': '60%', 'float': 'left'}, figure={}, clickData=None),
        dcc.Graph(id='accident-graph', style={'width': '40%', 'float': 'right'}, figure={}, clickData=None),
        ]),
    html.Div([
        # dcc.Graph(id='choropleth-map1', style={'width': '60%', 'float': 'left'}, figure=fig1),
    ])
])

    
