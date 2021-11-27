# Import libraries
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import json
pd.options.mode.chained_assignment = None
import plotly.express as px

# -- Import and clean data (importing csv into pandas)
dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
# dfa.columns = dfa.columns.str.title()
uk_cities = json.load(open("data/uk_districts.geojson", "r"))
dfa = dfa.dropna()

road_guide = pd.read_excel('data/Road-Safety-Open-Dataset-Data-Guide.xlsx')
district_names = road_guide[road_guide['field name'] == 'local_authority_district']
district_names.rename(columns={"code/format":"local_authority_district"}, inplace=True)
dfa['local_authority_district'] = dfa['local_authority_district'].map(district_names.set_index('local_authority_district')['label'])

# Create the Dash app
app = dash.Dash()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(children=[
    html.H2(children='UK Road Safety Dashboard'),
    dcc.Graph(id="choropleth"),
    dcc.Dropdown(id='year-dropdown',
                 options=[{'label': i, 'value': i}
                          for i in dfa['accident_year'].unique()],
                 value=2020),
    dcc.Graph(id='accidents-graph')
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='accidents-graph', component_property='figure'),
    Input(component_id='year-dropdown', component_property='value')
)
def update_graph(selected_year):
    filtered_dfa = dfa[dfa['accident_year'] == selected_year]
    filtered_dfa['date'] = pd.to_datetime(filtered_dfa['date'])
    dfa_grouped = (
        filtered_dfa.groupby(
            # normalize all dates to start of month
            filtered_dfa['date'].astype('datetime64[M]')
        )['accident_index'].count().rename('Total no of accidents').to_frame()
    )
    line_fig = px.line(dfa_grouped,
                       y='Total no of accidents',
                       hover_data=['Total no of accidents'],
                       title=f'Road Accidents in {selected_year}')
    return line_fig

@app.callback(
    Output(component_id='choropleth', component_property='figure'),
    Input(component_id='year-dropdown', component_property='value')
)
def display_choropleth(selected_year):
    df1 = dfa[['local_authority_ons_district', 'number_of_casualties']]
    df1['number_of_accidents'] = 1
    district_names = road_guide[road_guide['field name'] == 'local_authority_ons_district']
    district_names.rename(columns={"code/format": "local_authority_ons_district"}, inplace=True)
    ons_names = district_names[['local_authority_ons_district', 'label']]
    df_final = pd.merge(df1, ons_names, on="local_authority_ons_district", how="left")
    df_final = df_final.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()
    fig = px.choropleth_mapbox(df_final, locations="local_authority_ons_district",
                               featureidkey="properties.lad19cd",
                               geojson=uk_cities, color="number_of_accidents", hover_name="label",
                               mapbox_style="white-bg", zoom=4, center={"lat": 55, "lon": 0})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# ------------------------------------------------------------------------------
# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)