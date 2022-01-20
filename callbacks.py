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
from apps.exploration import df_final

uk_cities = json.load(open("data/uk_districts.geojson", "r"))
print("Callbacks")

@app.callback(
    [Output(component_id='choropleth-map', component_property='figure'),
     Output(component_id='accident-graph', component_property='figure')],
    [Input(component_id='choropleth-map', component_property='clickData'),
     Input(component_id='year', component_property='value'),
     Input(component_id='city', component_property='value')]
)
def update_graph(clickData, year, city):
    dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
    dfa = dfa.dropna()
    print(year)
    if year:
        dff = df_final[df_final['accident_year'].between(year[0], year[1])]
        dff = dff.drop(columns=['accident_year'])
        df_whole = dff
        dff = dff.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()

    if clickData is None and city is None:
        fig = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                   featureidkey="properties.lad19cd",
                                   geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                   color_continuous_scale=px.colors.sequential.YlOrBr,
                                   hover_name="label",
                                   mapbox_style="carto-positron",
                                   hover_data=['number_of_accidents', 'number_of_casualties'],
                                   zoom=4.5, center={"lat": 53.72, "lon": -1.96})

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

        dfa_grouped = (
            df_whole.groupby(
                # normalize all dates to start of month
                df_whole['date'].astype('datetime64[M]')
            )['accident_index'].count().rename('total no of accidents').to_frame()
        )
        dfa_grouped.head()
        accidents_fig = px.line(dfa_grouped,
                                y='total no of accidents',
                                hover_data=['total no of accidents'],
                                title='Accidents per Month in UK')

        return fig, accidents_fig

    else:
        if city is not None:
            print(city)
            location = dff.loc[dff['label'] == city, 'local_authority_ons_district'].iloc[0]
        else:
            print("Holaaa")
            json_str = json.dumps(clickData, indent=2)
            cities = json.loads(json_str)
            location = cities['points'][0]['location']
            city = cities['points'][0]['hovertext']

        for feature in uk_cities["features"]:
            if feature["properties"]["lad19cd"] == location:
                uk_city = feature
        # dff = dff[dff['local_authority_ons_district'] == uk_city["properties"]["lad19cd"]]
        # dff = dff.drop(columns=['accident_year'])
        # dff = dff.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()
        print(uk_city["properties"]["lat"])
        print(uk_city["properties"]["long"])
        dff = dff[dff['local_authority_ons_district'] == location]
        fig = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                   featureidkey="properties.lad19cd",
                                   geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                   color_continuous_scale=px.colors.sequential.YlOrBr,
                                   hover_name="label",
                                   mapbox_style="carto-positron",
                                   hover_data=['number_of_accidents', 'number_of_casualties'],
                                   zoom=8,
                                   center={"lat": uk_city["properties"]["lat"], "lon": uk_city["properties"]["long"]})

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

        filtered_dfa = df_whole[df_whole['local_authority_ons_district'] == location]
        dfa_grouped = (
            filtered_dfa.groupby(
                # normalize all dates to start of month
                filtered_dfa['date'].astype('datetime64[M]')
            )['accident_index'].count().rename('total no of accidents').to_frame()
        )
        dfa_grouped.head()
        accidents_fig = px.line(dfa_grouped,
                                y='total no of accidents',
                                hover_data=['total no of accidents'],
                                title=f'Accidents per Month in {city}')

        return fig, accidents_fig



    # resp = json.loads(json_str)
    # return json.dumps(clickData, indent=2)
    # pairs = resp.items()
    # print(type(json_str))

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