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
import seaborn as sns
from plotly.subplots import make_subplots
from apps.exploration import df_final, acc_cas_veh_df
from apps.home import uk_cities

# Callback start in which there are multiple inputs and outputs for interaction
@app.callback(
    [Output(component_id='choropleth-map', component_property='figure'),
     Output(component_id='acc-cas-graph', component_property='figure'),
     Output(component_id='days-hours-graph', component_property='figure'),
     Output(component_id='severity-graph', component_property='figure'),
     Output(component_id='treemap-graph', component_property='figure'),
     Output(component_id='road-speed-graph', component_property='figure'),
     Output(component_id='violin-graph', component_property='figure'),
     Output(component_id='factors-graph', component_property='figure')],
    [Input(component_id='choropleth-map', component_property='clickData'),
     Input(component_id='severity-graph', component_property='clickData'),
     Input(component_id='year', component_property='value'),
     Input(component_id='city', component_property='value')]
)
# Update graph callback function
def update_graph(click_map, click_sev, year, city):

    if year:
        dff = df_final[df_final['accident_year'].between(year[0], year[1])]
        dfacv = acc_cas_veh_df[acc_cas_veh_df['accident_year'].between(year[0], year[1])]
        dff.drop(columns=['accident_year'],inplace=True)
        dfacv.drop(columns=['accident_year'], inplace=True)
        dff = dff.groupby(['local_authority_ons_district', 'label'], as_index=False).sum()

# Showing default graphs and map when click_data is none
    if click_map is None and city is None and click_sev is None:
        dff.rename(columns={'number_of_accidents': 'Number of accidents', 'number_of_casualties': 'Number of casualties'}, inplace=True)
        """Fig 1 === UK districts Choropleth map"""
        fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                   featureidkey="properties.lad19cd",
                                   geojson=uk_cities, color="Number of accidents", opacity=0.8,
                                   color_continuous_scale=px.colors.sequential.YlOrBr,
                                   hover_name="label",
                                   mapbox_style="carto-positron",
                                   hover_data=['Number of accidents', 'Number of casualties'],
                                   zoom=4.5, center={"lat": 53.72, "lon": -1.96})

        fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                          xaxis=dict(color='#9D9D9D',
                                     gridcolor='#9D9D9D'),
                          yaxis=dict(gridcolor='#9D9D9D',
                                     color="#9D9D9D"),
                          paper_bgcolor='#26232C',
                            font_color = 'white',
                          margin={'l': 40, 'b': 40, 't': 40, 'r': 0})


        """Fig 2 === Accidents / Casualties per year"""

        acc_per_year = dfacv.groupby(dfacv['date'].astype('datetime64[Y]')
                                        )['accident_index'].count().rename('Total Number of Accidents').to_frame()

        cas_per_year = (dfacv.groupby(dfacv['date'].astype('datetime64[Y]'))
                               ['number_of_casualties'].sum().rename('Total Number of Casualties').to_frame())
        acc_cas_per_year = pd.concat([acc_per_year, cas_per_year], axis=1)

        colors = {'A': '#fbd56e',
                  'B': '#782b05'}

        fig2 = go.Figure(
            data=[

                go.Bar(name='Accidents', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Accidents'], yaxis='y',
                       offsetgroup=1,marker={'color': colors['A']}),
                go.Bar(name='Casualties', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Casualties'], yaxis='y',
                       offsetgroup=2,marker={'color': colors['B']})
            ],
            layout={
                'yaxis': {'title': 'Accidents/Casualties Number'},
                'yaxis2': {'title': 'Casualties', 'overlaying': 'y', 'side': 'right'}
            }
        )

        # Change the bar mode
        fig2.update_layout(title_text= 'Accidents & Casualties per Year', barmode='group')
        fig2.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """Fig 3 === Accidents per Daytime and Weekday Heatmap"""

        dfacv['date'] = pd.to_datetime(dfacv['date'])
        weekday = dfacv['date'].dt.day_name()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # slice first and second string from time column
        dfacv['hour'] = dfacv['time'].str[0:2]
        # convert new column to numeric datetype
        dfacv['hour'] = pd.to_numeric(dfacv['hour'])
        # drop null values in our new column
        accidents_df = dfacv.dropna(subset=['hour'])
        # cast to integer values
        accidents_df['hour'] = accidents_df['hour'].astype('int')

        # define a function that turns the hours into daytime groups
        def when_was_it(hour):
            return str(hour)

        # apply thus function to our temporary hour column
        accidents_df['daytime'] = accidents_df['hour'].apply(when_was_it)
        daytime = accidents_df['daytime'].values
        timeslots = ["" + str(x) for x in range(0, 24)]
        daytime_week_table = accidents_df.groupby([daytime, weekday], sort=False).size()
        daytime_week_table = daytime_week_table.rename_axis(['Hour of the Day', 'Weekday']) \
            .unstack('Weekday') \
            .reindex(index=timeslots, columns=days)
        fig3 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='YlOrBr',
                         title="Accidents per Daytime and Weekday", aspect='auto')

        fig3.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """Fig 4 === CASUALTY SEVERITY"""
        cas_sev = (dfacv.groupby(['casualty_severity'])
                           ['accident_index'].count().rename('Total Number of Accidents').to_frame())
        data = cas_sev['Total Number of Accidents']
        labels = cas_sev.index
        colors = ['#782b05', '#d6710d', '#fbd56e']
        fig4 = px.pie(cas_sev, values=data, names=labels,  title="Casualties Severity")
        fig4.update_traces(hoverinfo='label+percent', textfont_size=20,
                           marker=dict(colors=colors, line=dict(color='#111111', width=1)))
        fig4.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')


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

        """Fig 5 === Casualties by Means of transport / Treemap"""
        dfacv['vehicle'] = dfacv['vehicle_type'].apply(vehicle)

        vehicle_type_casualties = (dfacv.groupby(['vehicle'])
                                   ['number_of_casualties'].sum().rename('Accidents').to_frame())
        vehicle_type_casualties.reset_index(inplace=True)
        colors2 = ['#782b05', '#de6900', '#e87900', '#f8b535', '#f9c84f', '#f1efc3']
        fig5 = px.treemap(vehicle_type_casualties, labels='vehicle', path=['vehicle'],
                          values='Accidents', color='vehicle', color_discrete_sequence=colors2,
                          title="Casualties by Means of Transport",hover_data=['Accidents'])
        fig5.update_layout(uniformtext=dict(minsize=11, mode='show'))
        fig5.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """Fig 6 === Road Type - Speed Limit """
        road_speed_df = (dfacv.groupby(['road_type', 'speed_limit'])['accident_index'].count().rename(
            'Accidents').to_frame())
        road_speed_df.reset_index(inplace=True)
        road_speed_df = road_speed_df[road_speed_df.road_type != 'Data missing or out of range']
        road_speed_df = road_speed_df[road_speed_df.speed_limit != 'Data missing or out of range']
        fig6 = px.bar(road_speed_df, x=road_speed_df['Accidents'], y=road_speed_df['road_type'],
                      color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
                      color_continuous_scale=px.colors.sequential.YlOrBr,
                      title="Number of Accidents per Road Type/Speed Limit", orientation='h')
        fig6.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """Fig 7 === VIOLIN PLOT for Sex vs Age of Casualty """

        df_violin = dfacv
        fig7 = go.Figure()
        fig7.add_trace(go.Violin(x=df_violin['casualty_class'][df_violin['sex_of_casualty'] == 'Male'],
                                y=df_violin['age_of_casualty'][df_violin['sex_of_casualty'] == 'Male'],
                                legendgroup='M', scalegroup='M', name='M',line_color='#fbd56e', opacity = 1))

        fig7.add_trace(go.Violin(x=df_violin['casualty_class'][df_violin['sex_of_casualty'] == 'Female'],
                                y=df_violin['age_of_casualty'][df_violin['sex_of_casualty'] == 'Female'],
                                legendgroup='F', scalegroup='F', name='F', line_color='#782b05', opacity= 1 ))

        fig7.update_traces(box_visible=True, meanline_visible=True)
        fig7.update_layout(title_text= 'Casualties Distribution among Casualty Class and Age', violinmode='group')
        fig7.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """Fig 8 === Accident factors sub-plots"""
        fig8 = make_subplots(rows=2, cols=2)

        dfa_grouped = (dfacv.groupby(['urban_or_rural_area'])['accident_index'].
                       count().rename('total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['urban_or_rural_area'], y=dfa_grouped['total_accidents'], width=0.4,
                   name="Urban or Rural area"),row=1, col=1)

        dfa_grouped = (dfacv.groupby(['road_surface_conditions'])['accident_index'].count().rename('total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['road_surface_conditions'], y=dfa_grouped['total_accidents'],
                             name="Road surface conditions"),row=1, col=2)
        dfa_grouped = (dfacv.groupby(['weather_conditions'])['accident_index'].count().rename('total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['weather_conditions'], y=dfa_grouped['total_accidents'], name="Weather conditions"),row=2, col=1)

        dfa_grouped = (dfacv.groupby(['light_conditions'])['accident_index'].count().rename('total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['light_conditions'], y=dfa_grouped['total_accidents'], name="Light conditions"),
            row=2, col=2)
        fig8.update_layout(height=600, width=600,
                          font=dict(size=8))
        fig8.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')


        return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8

    # Change map and graphs according to click_data
    else:
        if city is not None:
            location = dff.loc[dff['label'] == city, 'local_authority_ons_district'].iloc[0]
            filtered_dfacv = dfacv[dfacv['local_authority_ons_district'] == location]

            for feature in uk_cities["features"]:
                if feature["properties"]["lad19cd"] == location:
                    uk_city = feature

            dff = dff[dff['local_authority_ons_district'] == location]
            """Fig 1 === UK districts Choropleth map"""
            fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                        featureidkey="properties.lad19cd",
                                        geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                        color_continuous_scale=px.colors.sequential.YlOrBr,
                                        hover_name="label",
                                        mapbox_style="carto-positron",
                                        hover_data=['number_of_accidents', 'number_of_casualties'],
                                        zoom=8,
                                        center={"lat": uk_city["properties"]["lat"],
                                                "lon": uk_city["properties"]["long"]})

            fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                               xaxis=dict(color='#9D9D9D',
                                          gridcolor='#9D9D9D'),
                               yaxis=dict(gridcolor='#9D9D9D',
                                          color="#9D9D9D"),
                               paper_bgcolor='#26232C',
                               font_color='white',
                               margin={'l': 40, 'b': 40, 't': 40, 'r': 0})

            if click_sev is not None:
                json_str2 = json.dumps(click_sev, indent=2)
                severity = json.loads(json_str2)
                severity_label = severity['points'][0]['label']
                filtered_dfacv = filtered_dfacv[filtered_dfacv['casualty_severity'] == severity_label]

        # Extract location and severity from json click data
        else:
            if click_map is not None and click_sev is None:
                json_str = json.dumps(click_map, indent=2)
                cities = json.loads(json_str)
                location = cities['points'][0]['location']
                city = cities['points'][0]['hovertext']

                filtered_dfacv = dfacv[dfacv['local_authority_ons_district'] == location]

                for feature in uk_cities["features"]:
                    if feature["properties"]["lad19cd"] == location:
                        uk_city = feature

                dff = dff[dff['local_authority_ons_district'] == location]
                fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                            featureidkey="properties.lad19cd",
                                            geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                            color_continuous_scale=px.colors.sequential.YlOrBr,
                                            hover_name="label",
                                            mapbox_style="carto-positron",
                                            hover_data=['number_of_accidents', 'number_of_casualties'],
                                            zoom=8,
                                            center={"lat": uk_city["properties"]["lat"],
                                                    "lon": uk_city["properties"]["long"]})

                fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                                   xaxis=dict(color='#9D9D9D',
                                              gridcolor='#9D9D9D'),
                                   yaxis=dict(gridcolor='#9D9D9D',
                                              color="#9D9D9D"),
                                   paper_bgcolor='#26232C',
                                   font_color='white',
                                   margin={'l': 40, 'b': 40, 't': 40, 'r': 0})

            elif click_map is None and click_sev is not None:
                json_str2 = json.dumps(click_sev,indent=2)
                severity = json.loads(json_str2)
                severity_label = severity['points'][0]['label']
                filtered_dfacv = dfacv[dfacv['casualty_severity'] == severity_label]
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
                                   font_color='white',
                                   margin={'l': 40, 'b': 40, 't': 40, 'r': 0})

            else:
                json_str = json.dumps(click_map, indent=2)
                cities = json.loads(json_str)
                location = cities['points'][0]['location']
                city = cities['points'][0]['hovertext']
                json_str2 = json.dumps(click_sev,indent=2)
                severity = json.loads(json_str2)
                severity_label = severity['points'][0]['label']
                filtered_dfacv = dfacv[dfacv['local_authority_ons_district'] == location]
                filtered_dfacv = filtered_dfacv[filtered_dfacv['casualty_severity'] == severity_label]

                for feature in uk_cities["features"]:
                    if feature["properties"]["lad19cd"] == location:
                        uk_city = feature

                dff = dff[dff['local_authority_ons_district'] == location]
                fig1 = px.choropleth_mapbox(dff, locations="local_authority_ons_district",
                                            featureidkey="properties.lad19cd",
                                            geojson=uk_cities, color="number_of_accidents", opacity=0.8,
                                            color_continuous_scale=px.colors.sequential.YlOrBr,
                                            hover_name="label",
                                            mapbox_style="carto-positron",
                                            hover_data=['number_of_accidents', 'number_of_casualties'],
                                            zoom=8,
                                            center={"lat": uk_city["properties"]["lat"],
                                                    "lon": uk_city["properties"]["long"]})

                fig1.update_layout(plot_bgcolor='#26232C', modebar_color='#136d6d',
                                   xaxis=dict(color='#9D9D9D',
                                              gridcolor='#9D9D9D'),
                                   yaxis=dict(gridcolor='#9D9D9D',
                                              color="#9D9D9D"),
                                   paper_bgcolor='#26232C',
                                   font_color = 'white',
                                   margin={'l': 40, 'b': 40, 't': 40, 'r': 0})

        acc_per_year = filtered_dfacv.groupby(filtered_dfacv['date'].astype('datetime64[Y]')
                                        )['accident_index'].count().rename('Total Number of Accidents').to_frame()

        cas_per_year = (filtered_dfacv.groupby(filtered_dfacv['date'].astype('datetime64[Y]'))
                               ['number_of_casualties'].sum().rename('Total Number of Casualties').to_frame())
        acc_cas_per_year = pd.concat([acc_per_year, cas_per_year], axis=1)
        colors = {'A': '#fbd56e',
                  'B': '#782b05'}
        fig2 = go.Figure(
            data=[
                go.Bar(name='Accidents', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Accidents'], yaxis='y',
                       offsetgroup=1,marker={'color': colors['A']}),
                go.Bar(name='Casualties', x=acc_cas_per_year.index, y=acc_cas_per_year['Total Number of Casualties'], yaxis='y',
                       offsetgroup=2,marker={'color': colors['B']})
            ],
            layout={
                'yaxis': {'title': 'Accidents/Casualties Number'},
                'yaxis2': {'title': 'Casualties', 'overlaying': 'y', 'side': 'right'}
            }
        )
        # Change the bar mode
        if city is not None:
            fig2.update_layout(title_text= f'Accidents & Casualties per Year in {city}', barmode='group')
        else:
            fig2.update_layout(title_text='Accidents & Casualties per Year', barmode='group')

        fig2.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """GRAPH 3 --- Accidents per Daytime and Weekday Heatmap"""

        filtered_dfacv['date'] = pd.to_datetime(filtered_dfacv['date'])
        weekday = filtered_dfacv['date'].dt.day_name()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # slice first and second string from time column
        filtered_dfacv['hour'] = filtered_dfacv['time'].str[0:2]
        # convert new column to numeric datetype
        filtered_dfacv['hour'] = pd.to_numeric(filtered_dfacv['hour'])
        # drop null values in our new column
        accidents_df = filtered_dfacv.dropna(subset=['hour'])
        # cast to integer values
        accidents_df['hour'] = accidents_df['hour'].astype('int')

        # define a function that turns the hours into daytime groups
        def when_was_it(hour):
            return str(hour)

        # apply thus function to our temporary hour column
        accidents_df['daytime'] = accidents_df['hour'].apply(when_was_it)
        daytime = accidents_df['daytime'].values
        timeslots = ["" + str(x) for x in range(0, 24)]
        daytime_week_table = accidents_df.groupby([daytime, weekday], sort=False).size()
        daytime_week_table = daytime_week_table.rename_axis(['Hour of the Day', 'Weekday']) \
            .unstack('Weekday') \
            .reindex(index=timeslots, columns=days)

        # Show graph and plots when city selected in click data
        if city is not None:
            fig3 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='YlOrBr',
                             title=f"Accidents per Daytime and Weekday in {city}", aspect='auto')
        else:
            fig3 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='YlOrBr',
                             title="Accidents per Daytime and Weekday", aspect='auto')

        fig3.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        filtered_cas_sev = (filtered_dfacv.groupby(['casualty_severity'])
                           ['accident_index'].count().rename('Total Number of Accidents').to_frame())

        data = filtered_cas_sev['Total Number of Accidents']
        labels = filtered_cas_sev.index
        colors = ['#782b05', '#d6710d', '#fbd56e']

        if city is not None:
            fig4 = px.pie(filtered_cas_sev, values=data, names=labels,  title=f'Casualties Severity in {city}')
        else:
            fig4 = px.pie(filtered_cas_sev, values=data, names=labels, title='Casualties Severity')


        fig4.update_traces(hoverinfo='label+percent', textfont_size=20,
                           marker=dict(colors=colors, line=dict(color='#111111', width=1)))
        fig4.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        """GRAPH 5 --- Casualties by Means of transport / Treemap"""

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

        filtered_dfacv['vehicle'] = filtered_dfacv['vehicle_type'].apply(vehicle)

        vehicle_type_casualties = (filtered_dfacv.groupby(['vehicle'])
                                   ['number_of_casualties'].sum().rename('Accidents').to_frame())
        vehicle_type_casualties.reset_index(inplace=True)
        colors2 = ['#782b05', '#de6900', '#e87900', '#f8b535', '#f9c84f', '#f1efc3']
        if city is not None:
            fig5 = px.treemap(vehicle_type_casualties, labels='vehicle', path=['vehicle'],
                              values='Accidents', color='vehicle', color_discrete_sequence=colors2,
                              title=f'Casualties by Means of Transport in {city}',hover_data=['Accidents'])
        else:
            fig5 = px.treemap(vehicle_type_casualties, labels='vehicle', path=['vehicle'],
                              values='Accidents', color='vehicle', color_discrete_sequence=colors2,
                              title='Casualties by Means of Transport',hover_data=['Accidents'])

        fig5.update_layout(uniformtext=dict(minsize=11, mode='show'))
        fig5.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')


        """GRAPH 6 --- Road Type - Speed Limit """
        road_speed_df = (filtered_dfacv.groupby(['road_type', 'speed_limit'])['accident_index'].count().rename(
            'Accidents').to_frame())
        road_speed_df.reset_index(inplace=True)
        road_speed_df = road_speed_df[road_speed_df.road_type != 'Data missing or out of range']
        road_speed_df = road_speed_df[road_speed_df.speed_limit != 'Data missing or out of range']

        if city is not None:

            fig6 = px.bar(road_speed_df, x=road_speed_df['Accidents'], y=road_speed_df['road_type'],
                      color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
                      color_continuous_scale=px.colors.sequential.YlOrBr,
                      title=f'Number of Accidents per Road Type/Speed Limit in {city}',orientation='h')
        else:

            fig6 = px.bar(road_speed_df, x=road_speed_df['Accidents'], y=road_speed_df['road_type'],
                      color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
                      color_continuous_scale=px.colors.sequential.YlOrBr,
                      title=f'Number of Accidents per Road Type/Speed Limit',orientation='h')

        fig6.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        df_violin_filtered = filtered_dfacv
        fig7 = go.Figure()
        fig7.add_trace(go.Violin(x=df_violin_filtered['casualty_class'][df_violin_filtered['sex_of_casualty'] == 'Male'],
                                 y=df_violin_filtered['age_of_casualty'][df_violin_filtered['sex_of_casualty'] == 'Male'],
                                 legendgroup='M', scalegroup='M', name='M', line_color='#fbd56e'))

        fig7.add_trace(go.Violin(x=df_violin_filtered['casualty_class'][df_violin_filtered['sex_of_casualty'] == 'Female'],
                                 y=df_violin_filtered['age_of_casualty'][df_violin_filtered['sex_of_casualty'] == 'Female'],
                                 legendgroup='F', scalegroup='F', name='F', line_color='#782b05'))

        fig7.update_traces(box_visible=True, meanline_visible=True)
        fig7.update_layout(violinmode='group')
        fig7.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        fig8 = make_subplots(rows=2, cols=2)

        dfa_grouped = (dfacv.groupby(['urban_or_rural_area'])['accident_index'].
                       count().rename('total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['urban_or_rural_area'], y=dfa_grouped['total_accidents'], width=0.4,
                              name="Urban or Rural area"), row=1, col=1)

        dfa_grouped = (dfacv.groupby(['road_surface_conditions'])['accident_index'].count().rename(
            'total_accidents').reset_index())

        fig8.add_trace(go.Bar(x=dfa_grouped['road_surface_conditions'], y=dfa_grouped['total_accidents'],
                              name="Road surface conditions"), row=1, col=2)
        dfa_grouped = (
            dfacv.groupby(['weather_conditions'])['accident_index'].count().rename('total_accidents').reset_index())

        fig8.add_trace(
            go.Bar(x=dfa_grouped['weather_conditions'], y=dfa_grouped['total_accidents'], name="Weather conditions"),
            row=2, col=1)

        dfa_grouped = (
            dfacv.groupby(['light_conditions'])['accident_index'].count().rename('total_accidents').reset_index())

        fig8.add_trace(
            go.Bar(x=dfa_grouped['light_conditions'], y=dfa_grouped['total_accidents'], name="Light conditions"),
            row=2, col=2)
        fig8.update_layout(height=600, width=600,
                           font=dict(size=8))
        fig8.update_layout(plot_bgcolor='#26232C',
                           paper_bgcolor='#26232C',
                           font_color='white')

        return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8
