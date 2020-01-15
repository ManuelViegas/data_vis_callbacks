import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go

######################################################Data##############################################################


room_types = ['Entire home/apt', 'Private room', 'Hotel room', 'Shared room']
listings_amsterdam = pd.read_csv('C:/Users/Manuel Gay/Desktop/DataVisualization_Project/listings_amsterdam_clean.csv')
listings_lisbon=pd.read_csv('C:/Users/Manuel Gay/Desktop/DataVisualization_Project/listings_lisbon_cleansed.csv')
calendar_lisbon=pd.read_csv('C:/Users/Manuel Gay/Desktop/DataVisualization_Project/calendar_lisbon_clean.csv')
merge = pd.merge(calendar_lisbon.rename(columns={'listing_id':'id'}), listings_lisbon, on='id', how='left')
merge.dropna(axis=0, how='any', thresh=None, subset=None, inplace=True)
am_local_extact = listings_amsterdam.loc[listings_amsterdam['is_location_exact'] == 1]

room_options = [dict(label=room_type, value=room_type) for room_type in am_local_extact['room_type'].unique()]

##################################################APP###############################################################

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.H1('Airbnb Lisbon')
    ], className='Title'),

    html.Div([

        html.Div([

            html.Label('Room Choice'),
            dcc.Dropdown(
                id='Room_drop',
                options=room_options,
                value = ['Entire home/apt'],
                multi=True
            )

        ], className='column1 pretty'),

        html.Div([

            html.Div([dcc.Graph(id='Lines')], className='bar_plot pretty')

        ], className='column2')

    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='Map')], className='column3 pretty'),

        html.Div([dcc.Graph(id='Radar')], className='column3 pretty'),

        html.Div([dcc.Graph(id='Bar')], className='column3 pretty')

    ], className='row')

])

######################################################Callbacks#########################################################


@app.callback(
    [
        Output("Map", "figure"),
        Output("Radar", "figure"),
        Output("Bar", "figure"),
        Output("Lines", "figure"),
    ],
    [
        Input("Room_drop", "value")
    ]
)
def plot(room_type):
    #############################################  Map   ######################################################
    data_map_set=pd.DataFrame()
    for room in room_type:
        am_local_extact_rt = am_local_extact.loc[(am_local_extact['room_type'] == room)]
        data_map_set=pd.concat([data_map_set, am_local_extact_rt])


    data = go.Scattermapbox(
        lat=data_map_set['latitude'],
        lon=data_map_set['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='lightcoral',
            opacity=0.4
        ),
        name='',
        text=data_map_set[['name', 'room_type', 'rating', 'price']],
        hoverinfo='text',
        hovertemplate='Name: %{text[0]}<br>' + 'Type: %{text[1]}<br>' + 'Rating: %{text[2]}/10<br>' + 'Price: $%{text[3]}',
        hoverlabel=dict(bordercolor='white')
    )
    fig = go.Figure(data=data)

    layout_map = fig.update_layout(title='Amsterdam ',
                                   autosize=True,
                                   hovermode='closest',
                                   showlegend=False,
                                   mapbox=go.layout.Mapbox(
                                       accesstoken='pk.eyJ1IjoibWFudWVsdmllZ2FzIiwiYSI6ImNrNWVhYnU1azF3eTEza3JmZng1NnRteWQifQ.R21u1mUs94IiWfF-9F-9sA',
                                       bearing=0,
                                       center=go.layout.mapbox.Center(lat=52.373, lon=4.903),
                                       pitch=0,
                                       zoom=13,
                                       style='light'))

    ########################################################Radar##############################################
    data_radar_set = pd.DataFrame()
    for room in room_type:
        listings_lisbon_rt = listings_lisbon.loc[(listings_lisbon['room_type'] == room)]
        data_radar_set=pd.concat([data_radar_set, listings_lisbon_rt])

    scores_lisbon = round(data_radar_set.mean()[['score_clean', 'score_communication', 'score_location']], 1)
    scores_lisbon = pd.DataFrame(scores_lisbon)
    scores_lisbon = scores_lisbon.T

    rating_lisbon = round(data_radar_set.mean()['rating'], 1)

    data_radar = [go.Scatterpolar(r=scores_lisbon.iloc[0],
                                  theta=['Clean', 'Communication', 'Location'],
                                  fill='toself',
                                  name='Total Rating: 9.2/10',
                                  hovertemplate='%{theta} Score: %{r}/10',
                                  line=dict(color='lightcoral'),
                                  hoverlabel=dict(bordercolor='white'))]

    layout_radar = go.Layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10]),
                                        bgcolor='whitesmoke'),
                             showlegend=False)
    ##############################################Bar#################################################
    data_bar_set = pd.DataFrame()
    for room in room_type:
        listings_lisbon_rt = listings_lisbon.loc[(listings_lisbon['room_type'] == room)]
        data_bar_set = pd.concat([data_bar_set, listings_lisbon_rt])

    count_listings = pd.DataFrame(data_bar_set.groupby('neighbourhood').count())
    count_listings = count_listings.sort_values(by=['id'], ascending=False)
    count_listings.reset_index(inplace=True)
    count_listings = count_listings.iloc[0:15, 0:2]
    count_listings.columns = ['neighbourhood', 'id']
    count_listings.replace({'Misericrdia': 'Misericórdia', 'So Vicente': 'São Vicente', 'Santo Antnio': 'Santo António',
                            'Penha de Frana': 'Penha de França',
                            'S.Maria, S.Miguel, S.Martinho, S.Pedro Penaferrim': 'Santa Maria e São Miguel',
                            }, inplace=True)

    data_bar = dict(type='bar', x=count_listings['neighbourhood'], y=count_listings['id'])

    layout_bar = dict(title=dict(text='Number of Listings By Neighbourhood (Top 15)', xanchor='center', yanchor='top',
                                 y=0.9, x=0.5, font=dict(color='rgb(255,255,255)')), yaxis=dict(title='# Listings',
                                                                                                showgrid=False,
                                                                                                color='rgb(255,255,255)'),
                      paper_bgcolor='lightcoral', plot_bgcolor='lightcoral', colorway=['rgb(255,255,255)'],
                      xaxis=dict(showgrid=False, color='rgb(255,255,255)'))
######################################################Lines######################################################
    data_lines_set = pd.DataFrame()
    for room in room_type:
        merge_rt = merge.loc[(merge['room_type'] == room)]
        data_lines_set = pd.concat([data_lines_set, merge_rt])

    avg_price_lisbon = pd.DataFrame(data_lines_set.groupby('month')['price_x'].mean())
    avg_price_lisbon['month'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    avg_price_lisbon['month_num'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    line_data_lisbon = [dict(type='scatter', x=avg_price_lisbon['month_num'], y=avg_price_lisbon['price_x'])]

    line_layout = dict(title=dict(text='Average Price Per Month', xanchor='center', yanchor='top', y=0.9, x=0.5,
                                  font=dict(color='rgb(255,255,255)')),
                       xaxis=dict(title='Month', showgrid=False, color='rgb(255,255,255)',
                                  tickvals=[i for i in range(1, 13)],
                                  ticktext=list(avg_price_lisbon['month'])),
                       yaxis=dict(title='Price ($)', showgrid=False, color='rgb(255,255,255)'),
                       paper_bgcolor='lightcoral', plot_bgcolor='lightcoral',
                       colorway=['rgb(255,255,255)'])


    return go.Figure(data=fig, layout=layout_map), \
           go.Figure(data=data_radar, layout=layout_radar), \
           go.Figure(data=data_bar, layout=layout_bar), \
           go.Figure(data=line_data_lisbon, layout=line_layout)

if __name__ == '__main__':
    app.run_server(debug=True)