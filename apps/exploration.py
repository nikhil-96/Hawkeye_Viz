import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
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
# dfa.columns = dfa.columns.str.title()
uk_cities = json.load(open("data/uk_districts.geojson", "r"))
dfa = dfa.dropna()

road_guide = pd.read_excel('data/Road-Safety-Open-Dataset-Data-Guide.xlsx')
district_names = road_guide[road_guide['field name'] == 'local_authority_district']
district_names.rename(columns={"code/format":"local_authority_district"}, inplace=True)
dfa['local_authority_district'] = dfa['local_authority_district'].map(district_names.set_index('local_authority_district')['label'])

df1 = dfa[['local_authority_ons_district', 'number_of_casualties']]
df1['number_of_accidents'] = 1
district_names = road_guide[road_guide['field name'] == 'local_authority_ons_district']
district_names.rename(columns={"code/format": "local_authority_ons_district"}, inplace=True)
ons_names = district_names[['local_authority_ons_district', 'label']]
df_final = pd.merge(df1, ons_names, on="local_authority_ons_district", how="left")
df_final = df_final.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()
# px.set_mapbox_access_token(mapbox_access_token)
fig = px.choropleth_mapbox(df_final, locations="local_authority_ons_district",
                            featureidkey="properties.lad19cd",
                            geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                            color_continuous_scale=px.colors.sequential.YlOrBr,
                            hover_name="label",
                            mapbox_style="carto-positron", hover_data=['number_of_accidents', 'number_of_casualties'],
                            zoom=4.5, center={"lat":51, "lon": 0})

fig.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                      xaxis=dict(color='#9D9D9D',
                                 gridcolor='#9D9D9D'),
                      yaxis=dict(gridcolor='#9D9D9D',
                                 color="#9D9D9D"),
                      paper_bgcolor='#26232C',
                      legend_font_color='white',
                      legend_title_font_color='white',
                      title_font_color="white",
                      margin={'l': 40, 'b': 40, 't': 40, 'r': 0})


layout = html.Div([
    html.Div([
        dcc.Graph(id='choropleth-map', style={'width': '60%', 'float': 'left'}, figure=fig),
        html.Pre(id='click-data', style={'width': '40%', 'float': 'right'}),
        ]),
    html.Div([
        # dcc.Graph(id='choropleth-map1', style={'width': '60%', 'float': 'left'}, figure=fig1),
    ])
])

    
