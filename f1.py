# Script written in Python 3.10

try:
    import fastf1 as ff1
except ImportError as e:
    print(e)
import pandas as pd
import numpy as np

# Set path to cache downloaded telemetry data
# Default is off
def set_cache(path):
    ff1.Cache.enable_cache(path)

# Obtain basic information about events in the given year(s)
# If n_year > 0, information for consecutive years are retrieved
def get_events(start_year, n_year=0):
    years = np.linspace(start_year, start_year + n_year, int(n_year+1))
    schedule = pd.DataFrame()
    for i , y in enumerate(years):
        try:
            sch = ff1.get_event_schedule(int(y))
            if i == 0:
                schedule = sch
            else:
                schedule = pd.concat([schedule, sch], axis=0, ignore_index=True)
        except Exception:
            print('Error!!! Did not get schedule', int(y))
            continue
    return schedule

# Obtain driver race result from a particular event, by specifying year and round_num
def get_race_result(year, round_num):
    try:
        s = ff1.get_session(int(year), int(round_num), 'Race')
        s.load(laps=False, telemetry=False, weather=False, messages=False)
        return s.results
    except:
        print('Error!!! No results loaded', year, round_num)

# Get data for all the laps done by all drivers in a particular event.
# session_num is a string - e.g. 'Practice 1', 'Practice 2', 'Practice 3', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race'
# or their abbrev - e.g. 'session_num1', 'session_num2', 'session_num3', 'Q', 'S', 'SQ', 'R'
# timedelta64 are converted to string by default
def get_session_lap_data(year, round_num, session_num, time_to_str=False):
    try:
        s = ff1.get_session(int(year), int(round_num), session_num)
        s.load(laps=True,telemetry=False, weather=False, messages=False)
        if time_to_str:
            for i, t in enumerate(s.laps.dtypes):
                if 'time' in str(t):
                    s.laps.iloc[:,i] = s.laps.iloc[:,i].astype(str)
        return s.laps
    except:
        print('Error!!! No session lap data loaded', year, round_num, session_num)

# Get telemetry data for drivers in a particular event
# session_num is a string - e.g. 'Practice 1', 'Practice 2', 'Practice 3', 'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race'
# or their abbrev - e.g. 'session_num1', 'session_num2', 'session_num3', 'Q', 'S', 'SQ', 'R'
# driver_list can be None (for all drivers) or a list of strings specifying the drivers
# time_to_str - Default = False.  Converts time to string in the return data table
def get_session_telemetry_data(year, round_num, session_num, driver_list=None,time_to_str=False):
    try:
        s = ff1.get_session(int(year), int(round_num), session_num)
    except:
        print('Error!!! Cannot get session', year, round_num, session_num)
    else:
        s.load(laps=True, telemetry=True, weather=False, messages=False)

        race = pd.DataFrame()

        if driver_list is None:
            driver_list = s.car_data.keys()

        for k in driver_list:
            print('processing driver '+k+' data...')
            try:
                tel_k = s.car_data[k].add_distance().merge_channels(s.pos_data[k])
                laps_k = s.laps[s.laps['DriverNumber'] == k]

                for l in range(0,laps_k.shape[0]):
                    lap_to_add = tel_k.slice_by_lap(laps_k.iloc[l,:], interpolate_edges=True)
                    lap_to_add['LapNum'] = l
                    lap_to_add['DriverNumber'] = int(k)
                    lap_to_add['Team'] = laps_k['Team'].iloc[0]

                    if race.shape == (0,0):
                        race = lap_to_add
                    else:
                        race = pd.concat([race, lap_to_add], axis=0, ignore_index=True)

            except:
                continue
        
        race.reset_index(inplace=True)
        race.drop('index', axis=1,inplace=True)

        if time_to_str:
            for i, t in enumerate(race.dtypes):
                if 'time' in str(t):
                    race.iloc[:,i] = race.iloc[:,i].astype(str)
        return race

# get a list of drivers and the result for a particular session in a particular event
def get_driver_info(year, round_num, session_num):
    return get_race_result(year, round_num)[['DriverNumber','Abbreviation','TeamName','TeamColor','FirstName','LastName']]

