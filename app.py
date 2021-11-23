# Import libraries
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# -- Import and clean data (importing csv into pandas)
dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
dfa.columns = dfa.columns.str.title()

dfa = dfa.dropna()

# Create the Dash app
app = dash.Dash()

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(children=[
    html.H1(children='UK Road Safety Dashboard'),
    dcc.Dropdown(id='year-dropdown',
                 options=[{'label': i, 'value': i}
                          for i in dfa['Accident_Year'].unique()],
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
    filtered_dfa = dfa[dfa['Accident_Year'] == selected_year]
    filtered_dfa['Date'] = pd.to_datetime(filtered_dfa['Date'])
    dfa_grouped = (
        filtered_dfa.groupby(
            # normalize all dates to start of month
            filtered_dfa['Date'].astype('datetime64[M]')
        )['Accident_Index'].count().rename('Total no of accidents').to_frame()
    )
    line_fig = px.line(dfa_grouped,
                       y='Total no of accidents',
                       hover_data=['Total no of accidents'],
                       title=f'Road Accidents in {selected_year}')
    return line_fig

# ------------------------------------------------------------------------------
# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)