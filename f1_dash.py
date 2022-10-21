import f1
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import plotly.express as px

# set a path to cache data for fast retrieval after the first download
f1.set_cache('/Volumes/Kalok/Data Science/f1data/cache/')

start_year = 2008
end_year = 2023

h1_style = {
    'textAlign':'center',
    'color':'#FFFFFF',
    'font-size':40,
}

h2_style = {
    'textAlign':'center',
    'color':'#FFFFFF',
    'font-size':28,
}

page_style = {
    'backgroundColor':'#000000',
}

year_list = []
for y in range(2022,2008, -1):
    year_list.append({'label':str(y), 'value':y})

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


app.layout = html.Div(
    children = [
        html.H1(
            children='Formula 1 Fastest Laps',
            style=h1_style,
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2(children='Year',style=h2_style),
                        dcc.Dropdown(
                            id='year_dd',
                            options=year_list,
                            placeholder='Select A Year',
                        )
                    ],
                    style={'width':'33%','display':'inline-block'},
                ),
                html.Div(
                    children=[
                        html.H2(children='Grand Prix',style=h2_style),
                        dcc.Dropdown(
                            id='gp_dd',
                            options=[],
                            placeholder='Select Grand Prix',
                        ),
                    ],
                    style={'width':'33%','display':'inline-block'},
                ),
                html.Div(
                    children=[
                        html.H2(children='Session',style=h2_style),
                        dcc.Dropdown(
                            id='session_dd',
                            options=[],
                            placeholder='Select Session',
                        ),
                    ],
                    style={'width':'33%','display':'inline-block'},
                ),
            ],
            style={'display':'flex'},
        ),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(id='plot1'),
                    style={'width':'70%','display':'inline-block'},
                ),
                html.Div(
                    children=dcc.Dropdown(
                        id='driver_list',
                        options=[],
                        placeholder='Select Driver(s)',
                        multi=True,
                    ),
                    style={'width':'30%','display':'inline-block'},
                ),
            ],
            style={'display':'flex'},
        ),
        html.Br(),
        html.Div(
            html.Button(id='submit',n_clicks=0,children='Submit')
        ),
        dcc.Store(id='events_info'),
    ],
    style = page_style,
)

# store events info
@app.callback(Output('events_info','data'),
              Input('year_dd','value'))
def get_events_info(year):
    if year is None:
        raise PreventUpdate
    else:
        events = f1.get_events(int(year))
        return events.to_json(date_format='iso',orient='split')

# update grand prix locations
@app.callback(Output('gp_dd','options'),
              Input('events_info','data'))
def get_gp_list(json_data):
    events = pd.read_json(json_data, orient='split')
    event_loc = events['Location']
    event_round_num = events['RoundNumber']
    options = []
    for loc, round_num in zip(event_loc, event_round_num):
        options.append({'label':loc,'value':round_num})
    return options

# update session list
@app.callback(Output('session_dd','options'),
              [Input('events_info','data'),
               Input('gp_dd','value')])
def get_session_list(json_data, round_num):
    if round_num is None:
        raise PreventUpdate
    else:
        events = pd.read_json(json_data, orient='split')
        event = events[events['RoundNumber']==round_num].reset_index()
        options = []
        for session_num in range(1,6):
            session_no_str = 'Session'+str(session_num)
            options.append({'label':event.loc[0,session_no_str],'value':session_no_str})
        return options

# update driver list
@app.callback(Output('driver_list','options'),
              [Input('year_dd','value'),
               Input('gp_dd','value'),
               Input('session_dd','value')])
def get_driver_list(year, round_num, session):
    if session is None:
        raise PreventUpdate
    else:
        driver_list = f1.get_driver_info(year, round_num, session)
        options = []
        for first, last, abbrev in zip(driver_list['FirstName'],driver_list['LastName'],driver_list['DriverNumber']):
            options.append({'label':first+" "+last,'value':abbrev})
        return options

# update plot
@app.callback(Output('plot1','figure'),
              Input('submit','n_clicks'),
              State('year_dd','value'),
              State('gp_dd','value'),
              State('session_dd','value'),
              State('driver_list','value'))
def get_plot(n_clicks,year,round_num,session, drivers):
    if session is None or year is None or round_num is None:
        raise PreventUpdate
    else:
        session_num = session[7:8]
        tel = f1.get_session_telemetry_data(int(year),int(round_num),int(session_num),driver_list=drivers)
        lap = f1.get_session_lap_data(int(year),int(round_num),int(session_num))

        best_lap = lap[lap['DriverNumber'].isin(drivers)][lap['IsPersonalBest']==True][['Driver','DriverNumber','LapNumber']]
        best_lap['LapNumber'] = lap['LapNumber'].astype(int)
        best_lap['DriverNumber'] = lap['DriverNumber'].astype(int)
        print(best_lap)
        print(best_lap.dtypes)

        best_tel = pd.merge(tel, best_lap, how='right', left_on=['DriverNumber','LapNum'], right_on=['DriverNumber','LapNumber'])
        best_tel.dropna(inplace=True, axis=0)
        minDist = best_tel[['DriverNumber','Distance']].groupby('DriverNumber').min().rename(columns={'Distance':'min_dist'})

        best_tel = pd.merge(best_tel, minDist, how='left', on='DriverNumber')
        print(best_tel.describe())
        print(best_tel.dtypes)
        
        best_tel['plot_distance'] = best_tel['Distance'] - best_tel['min_dist']
        print(best_tel[['Distance','min_dist','plot_distance']].describe())
        print(best_tel['DriverNumber'].unique())
        
        return px.line(best_tel, x='plot_distance',y='Speed',color='Driver')

if __name__=='__main__':
    app.run_server()
