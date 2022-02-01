# Import libraries
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

accidents_df = pd.read_csv('data/dft-road-casualty-statistics-accident-last-5-years.csv')
print('Accidents 2016-2020 Dataframe')
print('Records:', accidents_df.shape[0], '\nColumns:', accidents_df.shape[1])

casualties_df = pd.read_csv('data/dft-road-casualty-statistics-casualty-last-5-years.csv')
print('Casualties 2016-2020 Dataframe')
print('Records:', casualties_df.shape[0], '\nColumns:', casualties_df.shape[1])

vehicles_df = pd.read_csv('data/dft-road-casualty-statistics-vehicle-last-5-years.csv')
print('Vehicles 2016-2020 Dataframe')
print('Records:', vehicles_df.shape[0], '\nColumns:', vehicles_df.shape[1])

""" GRAPH 1 --- Accidents per weekday and year - Heatmap """

accidents_df['date'] = pd.to_datetime(accidents_df['date'])
weekday = accidents_df['date'].dt.day_name()
year = accidents_df['date'].dt.year
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
accident_table = accidents_df.groupby([year, weekday]).size()
accident_table = accident_table.rename_axis(['Year', 'Weekday'])\
                               .unstack('Weekday')\
                               .reindex(columns=days)
fig1 = px.imshow(accident_table, text_auto=False,color_continuous_scale='reds', title="Accidents per Year and Weekday")
fig1.show()

"""GRAPH 2 --- Total Number of Accidents/Casualties per Year"""
accidents_per_year = (accidents_df.groupby(accidents_df['accident_year'])
                      ['accident_index'].count().rename('Total Number of Accidents').to_frame())

casualties_per_year = (accidents_df.groupby(accidents_df['accident_year'])
                      ['number_of_casualties'].sum().rename('Total Number of Casualties').to_frame())
# fig3 = px.bar(casualties_per_year, x=casualties_per_year.index, y= casualties_per_year['Total Number of Casualties'],text_auto='.2s')
# fig3.show()
df = pd.concat([accidents_per_year, casualties_per_year], axis=1)
print(df)
fig2 = go.Figure(
    data=[
        go.Bar(name='Accidents', x=df.index, y=df['Total Number of Accidents'], yaxis='y',
               offsetgroup=1),
        go.Bar(name='Casualties', x=df.index, y=df['Total Number of Casualties'], yaxis='y',
               offsetgroup=2)
    ],
    layout={
        'yaxis': {'title': 'Accidents/Casualties Number'},
        'yaxis2': {'title': 'Casualties', 'overlaying': 'y', 'side': 'right'}
    }
)
# Change the bar mode
fig2.update_layout(barmode='group')
fig2.show()

#Match the numerical values with the respective labels
road_safety_guide = pd.read_excel("C:/Users/user/Desktop/TU Eindhoven/Q2/Visualization/Road_safety_data_Visualization/data/Road-Safety-Open-Dataset-Data-Guide.xlsx")

for i in range(len(road_safety_guide['field name'])):
    for header in list(accidents_df):
        if road_safety_guide['field name'][i] == header and not pd.isna(road_safety_guide['code/format'][i]):
            accidents_df[header].replace(road_safety_guide['code/format'][i], road_safety_guide['label'][i], inplace=True)

    for header in list(casualties_df):
        if road_safety_guide['field name'][i] == header and not pd.isna(road_safety_guide['code/format'][i]):
            casualties_df[header].replace(road_safety_guide['code/format'][i], road_safety_guide['label'][i], inplace=True)

"""GRAPH 3 --- Accident severity Graph"""
cas_severity_df = (casualties_df.groupby(['casualty_severity'])
                      ['accident_index'].count().rename('Total Number of Accidents').to_frame())
#cas_severity_df.reset_index(inplace=True)
#print(cas_severity_df)
data = cas_severity_df['Total Number of Accidents']
labels = cas_severity_df.index
colors = ['red', 'darkorange', 'gold']
fig3 = px.pie(cas_severity_df, values=data, names=labels,hole=0.5,title="Casualties Severity")
fig3.update_traces(hoverinfo='label+percent', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=1)))
fig3.show()

"""GRAPH 4 --- Accidents per Daytime and Weekday Heatmap"""

accidents_df['date'] = pd.to_datetime(accidents_df['date'])
weekday = accidents_df['date'].dt.day_name()
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# slice first and second string from time column
accidents_df['hour'] = accidents_df['time'].str[0:2]
# convert new column to numeric datetype
accidents_df['hour'] = pd.to_numeric(accidents_df['hour'])
# drop null values in our new column
accidents_df = accidents_df.dropna(subset=['hour'])
# cast to integer values
accidents_df['hour'] = accidents_df['hour'].astype('int')
# define a function that turns the hours into daytime groups
def when_was_it(hour):
    if hour >= 5 and hour < 10:
        return "morning rush (5:00-10:00)"
    elif hour >= 10 and hour < 15:
        return "office hours (10:00-15:00)"
    elif hour >= 15 and hour < 19:
        return "afternoon rush (15:00-19:00)"
    elif hour >= 19 and hour < 23:
        return "evening (19:00-23:00)"
    else:
        return "night (23:00-5:00)"

# apply thus function to our temporary hour column
accidents_df['daytime'] = accidents_df['hour'].apply(when_was_it)
daytime = accidents_df['daytime'].values
timeslots = ['morning rush (5:00-10:00)','office hours (10:00-15:00)','afternoon rush (15:00-19:00)',
             'evening (19:00-23:00)','night (23:00-5:00)']
daytime_week_table = accidents_df.groupby([daytime, weekday],sort=False).size()
daytime_week_table = daytime_week_table.rename_axis(['daytime', 'weekday'])\
                               .unstack('weekday')\
                               .reindex(index = timeslots, columns=days)

fig4 = px.imshow(daytime_week_table, text_auto=False, color_continuous_scale='PuBu',title="Accidents per Daytime and Weekday")
fig4.show()

#Merge accidents + casualties + vehicles on keys: ACCIDENT_INDEX, VEHICLE_REFERENCE, ACCIDENT_YEAR, ACCIDENT_REFERENCE
casualty_vehicle_df = casualties_df.merge(vehicles_df, on=['accident_index','vehicle_reference','accident_year','accident_reference'],how='inner')
print('Records:', casualty_vehicle_df.shape[0], '\nColumns:', casualty_vehicle_df.shape[1])

acc_cas_veh_df = casualty_vehicle_df.merge(accidents_df, on=['accident_index','accident_year','accident_reference'],how='inner')
print('Records:', acc_cas_veh_df.shape[0], '\nColumns:', acc_cas_veh_df.shape[1])

for i in range(len(road_safety_guide['field name'])):
    for header in list(acc_cas_veh_df):
        if road_safety_guide['field name'][i] == header and not pd.isna(road_safety_guide['code/format'][i]):
            acc_cas_veh_df[header].replace(road_safety_guide['code/format'][i], road_safety_guide['label'][i], inplace=True)

def vehicle(veh_type):
    if veh_type == 'Car' or veh_type == 'Taxi/Private hire car':
        return "Car"
    elif (veh_type == 'Motorcycle 50cc and under') or  (veh_type =='Mobility scooter')or (veh_type =='Motorcycle - unknown cc') or (veh_type == 'Motorcycle 125cc and under')or (veh_type =='Motorcycle 50cc and under') or (veh_type == 'Motorcycle over 125cc and up to 500cc')or (veh_type =='Motorcycle over 500cc'):
        return "Motorcycle"
    elif veh_type == 'Bus or coach (17 or more pass seats)' or veh_type == 'Minibus (8 - 16 passenger seats)':
        return "Bus"
    elif veh_type == 'Agricultural vehicle' or veh_type =='Goods 7.5 tonnes mgw and over' or veh_type =='Goods over 3.5t. and under 7.5t' or veh_type == 'Van / Goods 3.5 tonnes mgw or under':
        return "Truck"
    else:
        return "Other Vehicle"

"""GRAPH 5 --- Casualties by Means of transport / Treemap"""
acc_cas_veh_df['vehicle'] = acc_cas_veh_df['vehicle_type'].apply(vehicle)

vehicle_type_casualties = (acc_cas_veh_df.groupby(['vehicle'])
                      ['number_of_casualties'].sum().rename('Accidents').to_frame())
print(vehicle_type_casualties)
vehicle_type_casualties.reset_index(inplace=True)
fig5 = px.treemap(vehicle_type_casualties, labels= 'vehicle',path=['vehicle'],
                  values='Accidents',color='vehicle',color_discrete_sequence =px.colors.qualitative.Plotly,
                  title="Casualties by Means of Transport")
fig5.update_layout(uniformtext=dict(minsize=20,mode='show'))
fig5.show()

"""GRAPH 6 --- Road Type - Speed Limit """

road_speed_df = (acc_cas_veh_df.groupby(['road_type','speed_limit'])['accident_index'].count().rename('Accidents').to_frame())
road_speed_df.reset_index(inplace=True)
road_speed_df = road_speed_df[road_speed_df.road_type != 'Data missing or out of range']
road_speed_df = road_speed_df[road_speed_df.speed_limit != 'Data missing or out of range']
print(road_speed_df)
# road_speed_table = road_speed_df.unstack('speed_limit')
#road_speed_df = (acc_cas_veh_df.groupby('road_type')['accident_index'].count().to_frame())
fig6 = px.bar(road_speed_df, x=road_speed_df['road_type'], y=road_speed_df['Accidents'],
              color=road_speed_df['speed_limit'], text=road_speed_df['speed_limit'],
              color_discrete_sequence= px.colors.sequential.Plasma_r,title="Number of Accidents per Road Type (Speed Limit Hue)")
fig6.show()
