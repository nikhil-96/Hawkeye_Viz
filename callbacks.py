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
from apps.exploration import df_final, acc_cas_veh_df

uk_cities = json.load(open("data/uk_districts.geojson", "r"))
print("Callbacks")

@app.callback(
    [Output(component_id='choropleth-map', component_property='figure'),
     Output(component_id='acc-cas-graph', component_property='figure'),
     Output(component_id='days-hours-graph', component_property='figure'),
     Output(component_id='severity-graph', component_property='figure'),
     Output(component_id='treemap-graph', component_property='figure'),
     Output(component_id='road-speed-graph', component_property='figure')],
    [Input(component_id='choropleth-map', component_property='clickData'),
     Input(component_id='year', component_property='value'),
     Input(component_id='city', component_property='value')]
     # Input(component_id='severity-graph',component_property='clickData')]
)
def update_graph(clickData, year, city):
    # dfa = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
    # dfa = dfa.dropna()
    print(year)
    if year:
        dff = df_final[df_final['accident_year'].between(year[0], year[1])]
        dfacv = acc_cas_veh_df[acc_cas_veh_df['accident_year'].between(year[0], year[1])]
        dff.drop(columns=['accident_year'],inplace=True)
        dfacv.drop(columns=['accident_year'], inplace=True)
        df_whole = dff
        dff = dff.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()

    if clickData is None and city is None:
        fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                   featureidkey="properties.lad19cd",
                                   geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                   color_continuous_scale=px.colors.sequential.YlOrBr,
                                   hover_name="label",
                                   mapbox_style="carto-positron",
                                   hover_data=['number_of_accidents', 'number_of_casualties'],
                                   zoom=4.5, center={"lat": 53.72, "lon": -1.96})

        fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                          xaxis=dict(color='#9D9D9D',
                                     gridcolor='#9D9D9D'),
                          yaxis=dict(gridcolor='#9D9D9D',
                                     color="#9D9D9D"),
                          paper_bgcolor='#26232C',
                          legend_font_color='white',
                          legend_title_font_color='white',
                          title_font_color="white",
                          margin={'l': 40, 'b': 40, 't': 40, 'r': 0})


        """GRAPH 2 --- Accidents / Casualties per year"""

        acc_per_year = df_whole.groupby(df_whole['date'].astype('datetime64[Y]')
                                        )['accident_index'].count().rename('Total Number of Accidents').to_frame()

        cas_per_year = (df_whole.groupby(df_whole['date'].astype('datetime64[Y]'))
                               ['number_of_casualties'].sum().rename('Total Number of Casualties').to_frame())
        acc_cas_per_year = pd.concat([acc_per_year, cas_per_year], axis=1)

        # fig2 = px.line(acc_cas_per_year,
        #                         y=acc_cas_per_year['Total Number of Accidents'],
        #                         hover_data=acc_cas_per_year['Total Number of Accidents'],
        #                         title='Accidents per Month in UK')
        #
        # fig2.add_scatter(y=acc_cas_per_year['Total Number of Casualties'], mode='lines')

        # dict_of_fig = dict({"layout": {"title": {"text": "A Figure Specified By A Graph Object With A Dictionary"}}})
        fig2 = go.Figure(
            data=[
                go.Bar(name='Accidents', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Accidents'], yaxis='y',
                       offsetgroup=1),
                go.Bar(name='Casualties', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Casualties'], yaxis='y',
                       offsetgroup=2)
            ],
            layout={
                'yaxis': {'title': 'Accidents/Casualties Number'},
                'yaxis2': {'title': 'Casualties', 'overlaying': 'y', 'side': 'right'}
            }
        )

        # Change the bar mode
        fig2.update_layout(title_text= 'Accidents & Casualties per Year', barmode='group')
        # fig2.add_trace()

        """GRAPH 3--- Accidents per Daytime and Weekday Heatmap"""

        df_whole['date'] = pd.to_datetime(df_whole['date'])
        weekday = df_whole['date'].dt.day_name()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # slice first and second string from time column
        df_whole['hour'] = df_whole['time'].str[0:2]
        # convert new column to numeric datetype
        df_whole['hour'] = pd.to_numeric(df_whole['hour'])
        # drop null values in our new column
        accidents_df = df_whole.dropna(subset=['hour'])
        # cast to integer values
        accidents_df['hour'] = accidents_df['hour'].astype('int')

        # define a function that turns the hours into daytime groups
        def when_was_it(hour):
            if hour >= 5 and hour < 10:
                return "Morning Rush"
            elif hour >= 10 and hour < 15:
                return "Office Hours"
            elif hour >= 15 and hour < 19:
                return "Afternoon Rush"
            elif hour >= 19 and hour < 23:
                return "Evening"
            else:
                return "Night"

        # apply thus function to our temporary hour column
        accidents_df['daytime'] = accidents_df['hour'].apply(when_was_it)
        daytime = accidents_df['daytime'].values
        timeslots = ['Morning Rush', 'Office Hours', 'Afternoon Rush','Evening', 'Night']
        daytime_week_table = accidents_df.groupby([daytime, weekday], sort=False).size()
        daytime_week_table = daytime_week_table.rename_axis(['Daytime', 'Weekday']) \
            .unstack('Weekday') \
            .reindex(index=timeslots, columns=days)
        fig3 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='PuBu',
                         title="Accidents per Daytime and Weekday")


        """GRAPH 4 -- CASUALTY SEVERITY"""
        cas_sev = (dfacv.groupby(['casualty_severity'])
                           ['accident_index'].count().rename('Total Number of Accidents').to_frame())
        # cas_severity_df.reset_index(inplace=True)
        # print(cas_severity_df)
        data = cas_sev['Total Number of Accidents']
        labels = cas_sev.index
        colors = ['red', 'darkorange', 'gold']
        fig4 = px.pie(cas_sev, values=data, names=labels, hole=0.5, title="Casualties Severity")
        fig4.update_traces(hoverinfo='label+percent', textfont_size=20,
                           marker=dict(colors=colors, line=dict(color='#111111', width=1)))


        def vehicle(veh_type):
            if veh_type in range(8,10):
                return "Car"
            elif veh_type in range(0,6) or veh_type == 22 or veh_type == 23:
                return "Motorcycle"
            elif veh_type in range(10,12):
                return "Bus"
            elif veh_type == 17 or veh_type in range(19,22) or veh_type == 113:
                return "Truck"
            else:
                return "Other Vehicle"

        """GRAPH 5 --- Casualties by Means of transport / Treemap"""
        dfacv['vehicle'] = dfacv['vehicle_type'].apply(vehicle)

        vehicle_type_casualties = (dfacv.groupby(['vehicle'])
                                   ['number_of_casualties'].sum().rename('Accidents').to_frame())
        vehicle_type_casualties.reset_index(inplace=True)
        fig5 = px.treemap(vehicle_type_casualties, labels='vehicle', path=['vehicle'],
                          values='Accidents', color='vehicle', color_discrete_sequence=px.colors.qualitative.Plotly,
                          title="Casualties by Means of Transport",hover_data=['Accidents'])
        fig5.update_layout(uniformtext=dict(minsize=11, mode='show'))

        """GRAPH 6 --- Road Type - Speed Limit """
        road_speed_df = (dfacv.groupby(['road_type', 'speed_limit'])['accident_index'].count().rename(
            'Accidents').to_frame())
        road_speed_df.reset_index(inplace=True)
        road_speed_df = road_speed_df[road_speed_df.road_type != 'Data missing or out of range']
        road_speed_df = road_speed_df[road_speed_df.speed_limit != 'Data missing or out of range']
        fig6 = px.bar(road_speed_df, x=road_speed_df['Accidents'], y=road_speed_df['road_type'],
                      color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
                      color_discrete_sequence=px.colors.sequential.Plasma_r,
                      title="Number of Accidents per Road Type/Speed Limit", orientation='h')


        return fig1, fig2, fig3, fig4, fig5, fig6

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
        fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                   featureidkey="properties.lad19cd",
                                   geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                   color_continuous_scale=px.colors.sequential.YlOrBr,
                                   hover_name="label",
                                   mapbox_style="carto-positron",
                                   hover_data=['number_of_accidents', 'number_of_casualties'],
                                   zoom=8,
                                   center={"lat": uk_city["properties"]["lat"], "lon": uk_city["properties"]["long"]})

        fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                          xaxis=dict(color='#9D9D9D',
                                     gridcolor='#9D9D9D'),
                          yaxis=dict(gridcolor='#9D9D9D',
                                     color="#9D9D9D"),
                          paper_bgcolor='#26232C',
                          legend_font_color='white',
                          legend_title_font_color='white',
                          title_font_color="white",
                          margin={'l': 40, 'b': 40, 't': 40, 'r': 0})

        #Filter by location

        filtered_dfa = df_whole[df_whole['local_authority_ons_district'] == location]
        filtered_dfacv = dfacv[dfacv['local_authority_ons_district'] == location]

        # dfa_grouped = (
        #     filtered_dfa.groupby(
        #         # normalize all dates to start of month
        #         filtered_dfa['date'].astype('datetime64[M]')
        #     )['accident_index'].count().rename('Number of Accidents').to_frame()
        # )
        # fig2 = px.scatter(dfa_grouped,
        #                         y='Number of Accidents',
        #                         hover_data=['Number of Accidents'],
        #                         title=f'Accidents per Month in {city}',trendline="rolling",
        #                         trendline_options=dict(window=6))
        acc_per_year = filtered_dfa.groupby(filtered_dfa['date'].astype('datetime64[Y]')
                                        )['accident_index'].count().rename('Total Number of Accidents').to_frame()

        cas_per_year = (filtered_dfa.groupby(filtered_dfa['date'].astype('datetime64[Y]'))
                               ['number_of_casualties'].sum().rename('Total Number of Casualties').to_frame())
        acc_cas_per_year = pd.concat([acc_per_year, cas_per_year], axis=1)

        fig2 = go.Figure(
            data=[
                go.Bar(name='Accidents', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Accidents'], yaxis='y',
                       offsetgroup=1),
                go.Bar(name='Casualties', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Casualties'], yaxis='y',
                       offsetgroup=2)
            ],
            layout={
                'yaxis': {'title': 'Accidents/Casualties Number'},
                'yaxis2': {'title': 'Casualties', 'overlaying': 'y', 'side': 'right'}
            }
        )
        # Change the bar mode
        fig2.update_layout(title_text= f'Accidents & Casualties per Year in {city}', barmode='group')

        """GRAPH 3 --- Accidents per Daytime and Weekday Heatmap"""
        filtered_dfa['date'] = pd.to_datetime(filtered_dfa['date'])
        weekday = filtered_dfa['date'].dt.day_name()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        filtered_dfa['hour'] = filtered_dfa['time'].str[0:2]
        filtered_dfa['hour'] = pd.to_numeric(filtered_dfa['hour'])
        filtered_dfa = filtered_dfa.dropna(subset=['hour'])
        filtered_dfa['hour'] = filtered_dfa['hour'].astype('int')

        # define a function that turns the hours into daytime groups
        def when_was_it(hour):
            if hour >= 5 and hour < 10:
                return "Morning Rush"
            elif hour >= 10 and hour < 15:
                return "Office Hours"
            elif hour >= 15 and hour < 19:
                return "Afternoon Rush"
            elif hour >= 19 and hour < 23:
                return "Evening"
            else:
                return "Night"

        # apply thus function to our temporary hour column
        filtered_dfa['daytime'] = filtered_dfa['hour'].apply(when_was_it)
        daytime = filtered_dfa['daytime'].values
        timeslots = ['Morning Rush', 'Office Hours', 'Afternoon Rush','Evening', 'Night']
        daytime_week_table = filtered_dfa.groupby([daytime, weekday], sort=False).size()
        daytime_week_table = daytime_week_table.rename_axis(['Daytime', 'Weekday']) \
            .unstack('Weekday') \
            .reindex(index=timeslots, columns=days)
        fig3 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='PuBu',
                         title=f'Accidents per Daytime and Weekday in {city}')

        filtered_cas_sev = (filtered_dfacv.groupby(['casualty_severity'])
                           ['accident_index'].count().rename('Total Number of Accidents').to_frame())
        # cas_severity_df.reset_index(inplace=True)
        # print(cas_severity_df)
        data = filtered_cas_sev['Total Number of Accidents']
        labels = filtered_cas_sev.index
        colors = ['red', 'darkorange', 'gold']
        fig4 = px.pie(filtered_cas_sev, values=data, names=labels, hole=0.5, title=f'Casualties Severity in {city}')
        fig4.update_traces(hoverinfo='label+percent', textfont_size=20,
                           marker=dict(colors=colors, line=dict(color='#111111', width=1)))

        def vehicle(veh_type):
            if veh_type in range(8, 10):
                return "Car"
            elif veh_type in range(0, 6) or veh_type == 22 or veh_type == 23:
                return "Motorcycle"
            elif veh_type in range(10, 12):
                return "Bus"
            elif veh_type == 17 or veh_type in range(19, 22) or veh_type == 113:
                return "Truck"
            else:
                return "Other Vehicle"

        """GRAPH 5 --- Casualties by Means of transport / Treemap"""
        filtered_dfacv['vehicle'] = filtered_dfacv['vehicle_type'].apply(vehicle)

        vehicle_type_casualties = (filtered_dfacv.groupby(['vehicle'])
                                   ['number_of_casualties'].sum().rename('Accidents').to_frame())
        vehicle_type_casualties.reset_index(inplace=True)
        fig5 = px.treemap(vehicle_type_casualties, labels='vehicle', path=['vehicle'],
                          values='Accidents', color='vehicle', color_discrete_sequence=px.colors.qualitative.Plotly,
                          title=f'Casualties by Means of Transport in {city}',hover_data=['Accidents'])
        fig5.update_layout(uniformtext=dict(minsize=11, mode='show'))

        """GRAPH 6 --- Road Type - Speed Limit """
        road_speed_df = (filtered_dfacv.groupby(['road_type', 'speed_limit'])['accident_index'].count().rename(
            'Accidents').to_frame())
        road_speed_df.reset_index(inplace=True)
        road_speed_df = road_speed_df[road_speed_df.road_type != 'Data missing or out of range']
        road_speed_df = road_speed_df[road_speed_df.speed_limit != 'Data missing or out of range']

        fig6 = px.bar(road_speed_df, x=road_speed_df['Accidents'], y=road_speed_df['road_type'],
                      color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
                      color_discrete_sequence=px.colors.sequential.Plasma_r,
                      title=f'Number of Accidents per Road Type/Speed Limit in {city}',orientation='h')



        return fig1, fig2, fig3, fig4, fig5, fig6



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
