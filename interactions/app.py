import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash
import plotly.express as px

df = pd.read_csv('https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-accident-last-5-years.csv')

#add in dfa the data you want to map with the road guide data
df = df[['accident_index','accident_year','light_conditions','road_type']]
df['number_of_accidents'] = 1
df = df.groupby(["light_conditions","road_type"], as_index=False).sum()

print(df)

# data = {'light_conditions': ['bad', 'good', 'good', 'bad','bad','bad'],
#         'road_type': ['new', 'old', 'old', 'old','new','old'],
#         'number_of_accidents': [1,1,1,1,1,1]}
#
# df = pd.DataFrame(data)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id = 'light_conditions', figure={}, clickData=None
    ),
    dcc.Graph(id = 'road_type', figure={} , clickData=None
        )
])

@app.callback(
    Output(component_id='light_conditions', component_property='figure'),
    Input(component_id='road_type', component_property='clickData'),
)
def update_graph(clk_data):
    if clk_data is None:
        fig2 = px.bar(df, x=df['light_conditions'], y=df['number_of_accidents'])
        return fig2
    else:
        print(f'click data: {clk_data}')
        # print(f'selected data: {slct_data}')
        clk_road = clk_data['points'][0]['x']
        print(clk_road)
        dff2 = df[df.road_type == clk_road]
        fig2 = px.bar(dff2, x=dff2['light_conditions'], y=dff2['number_of_accidents'])
        return fig2

@app.callback(
    Output(component_id='road_type', component_property='figure'),
    Input(component_id='light_conditions', component_property='clickData'),
)
def update_graph(clk_data):
    if clk_data is None:
        fig2 = px.bar(df, x=df['road_type'], y=df['number_of_accidents'])
        return fig2
    else:
        print(f'click data: {clk_data}')
        # print(f'selected data: {slct_data}')
        clk_light = clk_data['points'][0]['x']
        print(clk_light)
        dff2 = df[df.light_conditions == clk_light]
        fig2 = px.bar(dff2, x=dff2['road_type'], y=dff2['number_of_accidents'])
        return fig2

if __name__ == '__main__':
    app.run_server(debug=True)