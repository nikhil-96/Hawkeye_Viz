from app import app
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.express as px
import plotly.graph_objects as go
from plotly.tools import mpl_to_plotly
import json
import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
#
#
# """import data"""
#

#
#
@app.callback(
    Output('click-data', 'children'),
    [Input('choropleth-map', 'clickData')])
def display_click_data(clickData):
    json_str = json.dumps(clickData)
    resp = json.loads(json_str)
    return json.dumps(clickData, indent=2)
    # for x in resp:
    #     print(x['location'])

# @app.callback(Output('tabs-example-content', 'children'),
#               [Input('tabs-example', 'value')])
# def render_content(tab):
#     if tab == 'tab-1':
#         return html.Div([
#                html.Div([
#                         #Create drop down window for x-axis
#                         html.Div([html.H4('Show on x-axis:'),
#                                   dcc.Dropdown(
#                                      id='xaxis-col',
#                                      options=[{'label': i, 'value': i} for i in cont_vars],
#                                      value='Hematocrit',
#                                      clearable=False
#                                  )], style={'width': '17%','text-align': 'center', 'position':'relative', 'left':80, 'display': 'inline-block'}),
#
#                         #Create drop down window for y-axis
#                         html.Div([html.H4('Show on y-axis:'),
#                                   dcc.Dropdown(
#                                      id='yaxis-col',
#                                      options=[{'label': i, 'value': i} for i in cont_vars],
#                                      value='Hemoglobin',
#                                      clearable=False
#                                  )], style={'width': '17%','text-align': 'center','position':'relative', 'left':150,'display': 'inline-block'}),
#                      ],style={'padding': 20}),
#
#                 #Create graphic to show scatter plot
# #                 html.Div([html.H2('Scatter plot for all continuous test variables', style={'text-align': 'left','position':'relative', 'left':150}),
# #                           html.H2('title of boxplot', style={'position':'static', 'text-align': 'center'})]),
#

#
# #                 html.Div([html.H2('title of barchart',style={'text-align': 'left','position':'relative', 'left':150}),
# #                           html.H2('Distribution of positive cases over hospitalization', style={'text-align': 'right', 'position':'relative', 'left':50})]),
#
#                 html.Div([dcc.Graph(figure=fig_ageq, id='fig_ageq', style={'width': '45%', 'float': 'left', 'display': 'inline'}),
#                           dcc.Graph(figure=fig_2, id='fig_wards',style={'float': 'right', 'display': 'inline'})]),
# #                 html.Div([html.H2('blablablablbalblalbal',style={'text-align': 'left','position':'relative', 'left':150})]),
#                 html.Div([dcc.Graph(id='parallel-coord', style={'width': '100%','float': 'center','display': 'inline-block'})])
#
#
# ])
#     elif tab == 'tab-2':
#         return html.Div([html.H2('HEATMAP OF HISTORICAL COVID STRAINS AND select', style={'marginTop':30}),
#                          html.H2(' mean test records'),
#                          html.Div([html.H4('Select COVID test:', style={'marginTop':30}),
#                         dcc.Dropdown(
#                             id='covid-type',
#                             options=[{'label': i, 'value': i} for i in heatmap_cols],
#                             value='Test result COVID'
#                         )], style={'width': '48%', 'display': 'inline-block', 'float':'right'}),
#                 html.Div([dcc.Graph(id='covid-strain-heatmap', style={'width': '48%', 'display': 'inline-block', 'float': 'center'})],style={'padding': 30}),
#                 html.Div([html.Div([html.H2('Correlation heatmap for select patient characteristics', style={'marginTop':30}),
#                                    #Create multi-select window for correlation heat map of all variables
#                                    html.Div([html.H4('Select patient characteristics:'),
#                                              dcc.Dropdown(id='corr-matrix',
#                                                           options=[{'label': i, 'value': j} for i,j in zip(ht_cols, range(0, 74))],
#                                                           value=list(range(0,24)),multi=True,
#                                                           style={'backgroundColor': '#26232C'})], style={'backgroundColor': '#26232C'})
#                                    ]),
#                          dcc.Graph(id='correlation-heatmap-all-vars')])
# ])
#