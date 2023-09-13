"""
Note: change precip directory to a test directory for easy file
authentication. I would recommend choosing the sample
usage as I already have the results from those and can easily write
tests for it.

Standard Deviation is the sample standard deviation not a population
deviation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from chrpa.main import processing as main

# =============================================================================
# def test_parse_data_orig():
#     test_nc_file = 'precip/pr_HRM3_gfdl_1968010103.nc'
#     output = main.get_closest_point(
#         (36.7463169, -101.4838549),
#         test_nc_file, [0,0]
#         )
#     assert output['nc_xindex'] == 69
#     assert output['nc_yindex'] == 40
#     return
#
# def test_get_closest_point():
#     test_nc_file = 'precip/pr_HRM3_gfdl_1968010103.nc'
#     output = main.get_closest_point(
#         (36.7463169, -101.4838549),
#         test_nc_file, [0,0]
#         )
#     assert output['ws_lat'] == 36.62239456176758
#     assert output['ws_lon'] == -101.30980682373047
#     assert output['dist'] == 20.75454177359249
#     assert output['nc_xindex'] == 69
#     assert output['nc_yindex'] == 40
#     return
#
# def test_weather_data_calcs():
#     test_nc_file = 'precip/pr_HRM3_gfdl_1968010103.nc'
#     output = main.weather_data_calcs(test_nc_file, (69, 40), 'pr')
#     assert output[0][0] == 0.125
#     assert output[1][67] >= 3.9615727e-07 and output[1][67] <= 3.9615729e-07
#     return
#
# def test_make_ordered_time_weather_lists():
#     test_ncfiles = ['precip/pr_HRM3_gfdl_1968010103.nc',
#                     'precip/pr_HRM3_gfdl_1971010103.nc']
#     timelist, preciplist = main.make_ordered_time_weather_lists(test_ncfiles,
#                                                                 (69, 40), 'pr')
#
#     assert timelist[0][0] == 0.125
#     assert timelist[0][-1] == 1095.0
#     assert timelist[1][0] == 1095.125
#     assert timelist[1][-1] == 2920.0
#     assert preciplist[0][0] == 0
#     return
# =============================================================================

def test_timedelta_to_continous_w_weather():
    timelist = [[0, 1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10]]
    preciplist = [[1, 1, 2, 1, 2, 1],
                  [3, 2, 1, 3, 2]]
    timedelta_df = main.timedelta_to_continuous_w_weather(
        timelist,
        preciplist,
        'precip',
        '1968-01-01 00:00:00'
        )
    assert timedelta_df['time'][0] == datetime(1968, 1, 1)
    assert timedelta_df['precip'][0] == 1
    assert timedelta_df['precip'].iloc[-1] == preciplist[1][-1]
    assert len(timedelta_df['time']) == len(timedelta_df['precip'])
    return

def test_convert_preciprate_to_mm():
    test_df = pd.DataFrame({'time': [1,2], 'precip': [2, None]})
    precip_df_mm = main.convert_preciprate_to_mm(test_df, 5, 'precip')
    assert precip_df_mm['precip'][0] == 36000
    assert len(precip_df_mm['precip']) == 1
    return

def test_convert_to_daily():
    test_df = pd.DataFrame(
        {'time': [datetime(2022, 1, 1, 1),
                  datetime(2022, 1, 1, 6),
                  datetime(2022, 1, 1, 10),
                  datetime(2022, 1, 2, 1),
                  datetime(2022, 1, 2, 6),
                  datetime(2022, 1, 2, 10)],
         'weather': [4, 2, 0, 1, 3, 5]}
        )
    output = main.convert_to_daily(test_df, 'time', 'sum')
    assert output['weather'][0] == 6
    assert output['weather'][1] == 9
    return

def test_convert_to_mm_daily():
    test_df = pd.DataFrame(
        {'time': [datetime(2022, 1, 1, 0),
                  datetime(2022, 1, 1, 6),
                  datetime(2022, 1, 1, 9),
                  datetime(2022, 1, 2, 1),
                  datetime(2022, 1, 2, 6),
                  datetime(2022, 1, 2, 10)],
         'weather': [0, 2, 0, 1, 3, 5]}
        )
    output = main.convert_to_mm_daily(test_df, 5, 'time', 'weather', 'sum')
    assert output['weather'][0] == 36000
    return

def test_convert_uasvas_to_wind():
    test_df_1 = pd.DataFrame({'date': [1,2,3],
                              'weather': [3,5, None]})
    test_df_2 = pd.DataFrame({'date': [1,2,3],  # using pythogorean triples
                              'weather': [4,12, None]})
    convert_test_df = main.convert_uasvas_to_wind(test_df_1,
                                             test_df_2,
                                             'weather',
                                             'weather',
                                             'date',
                                             'wind')
    assert convert_test_df['wind'][0] == 5
    assert convert_test_df['wind'][1] == 13
    return

def test_summary_stat_fun():
    test_df_1 = pd.DataFrame({'date': [1,2,3,4,5],
                              'weather': [5,5,4,4,9]})
    test_df_2 = pd.DataFrame({'date': [1,2,3,4,5],
                              'weather': [9,9,8,7,6]})
    sum_1, sum_2 = main.summary_stat_fun(test_df_1, test_df_2, 'Model', 'Site')
    assert sum_1['min'][0] == 4
    assert sum_1['max'][0] == 9
    assert sum_1['mean'][0] == 5.4
    assert sum_1['sd'][0] <= 2.07365 and sum_1['sd'][0] >= 2.07363


    assert sum_2['min'][0] == 6
    assert sum_2['max'][0] == 9
    assert sum_2['mean'][0] == 7.8
    return

def test_get_annual_max():
    test_df = pd.DataFrame({'date': [datetime(2022, 1, 1, 1),
                            datetime(2022, 1, 1, 6),
                            datetime(2022, 1, 1, 10),
                            datetime(2023, 1, 2, 1),
                            datetime(2023, 1, 2, 6),
                            datetime(2023, 1, 2, 10)],
                            'weather': [4, 2, 0, 1, 3, 5]})
    test_rename = {'weather': 'MAX_weather'}
    output = main.get_annual_max(test_df, test_rename, 'mymodel', 'current')
    assert output['MAX_weather'][0] == 4
    assert output["MAX_weather"][1] == 5
    assert len(output['year']) == 2
    assert output['model'][0] == 'mymodel'

def test_myextremes():
    test_df = pd.DataFrame({'year' : [1978, 1979, 1980],
                            'precip' : [5,7,8]})

    rp_array = np.array([10, 56, 55, 54, 51])

    output = main.myextremes(test_df, rp_array, 'precip')

    for i in output['return value']:
        assert i <= 7.0002 and i >= 6.99999999
    return

def test_find_rl_location():
    test_df = pd.DataFrame(
        {'return period': [10.0, 56.0, 55.0, 54.0, 51.0],
         'return value': [7.1, 7.2, 7.1, 7.4, 7.1],
         'lower ci': [None] * 5,
         'upper ci': [None] * 5})
    assert main.find_rl_location(test_df, 7) == 0
    assert main.find_rl_location(test_df, 11) == 3
    return






