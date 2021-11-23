# Import libraries
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# -- Import and clean data (importing csv into pandas)
avocado = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')

# Create the Dash app
app = dash.Dash()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(children=[
    html.H1(children='UK Road Safety Dashboard'),
    dcc.Dropdown(id='geo-dropdown',
                 options=[{'label': i, 'value': i}
                          for i in avocado['geography'].unique()],
                 value='Las Vegas'),
    dcc.Graph(id='price-graph')
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='price-graph', component_property='figure'),
    Input(component_id='geo-dropdown', component_property='value')
)
def update_graph(selected_geography):
    filtered_avocado = avocado[avocado['geography'] == selected_geography]
    line_fig = px.line(filtered_avocado,
                       x='date', y='average_price',
                       color='type',
                       title=f'Avocado Prices in {selected_geography}')
    return line_fig


# ------------------------------------------------------------------------------
# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)