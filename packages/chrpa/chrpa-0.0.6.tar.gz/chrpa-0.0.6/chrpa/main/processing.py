"""
chrpa:  climate hazards return period analysis
"""

import os
import datetime
import pyextremes

import numpy as np
import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import great_circle


pd.set_option('display.max_columns', None)


def parse_data_orig(ncfilepath, offset):
    """
    Extracts latitude and longitude from a netCDF (network Common Data
    Form) format and returns them in a data frame

    Parameters
    ----------
    ncfilepath : str
        A filepath in the form of a string that points to the location
        of the netCDF file of interest

    offset : list
        Contains the lattitude and longitude offest in the form of
        [lat, lon]


    Returns
    -------
    Dictionary
        Dictionary with latitude and longitude components corresponding
        to the input file

    """

    ncfile = nc.Dataset(ncfilepath)

    nc_lat = ncfile.variables['lat'][:]
    nc_lat = np.ma.getdata(nc_lat) + offset[0]
    nc_lon = ncfile.variables['lon'][:]
    nc_lon = np.ma.getdata(nc_lon) + offset[1]

    data_dict = {'lat': nc_lat, 'lon': nc_lon}
    return data_dict

def get_closest_point(site_loc, ncfilepath, offset):
    """
    Finds the closest data point between location of interest
    (site_loc) and weather stations captured by .nc files
    (ncfilepath)

    Parameters
    ----------
    site_loc : tuple
        Latitude and longitude in the form of (lat, lon) for location
        of interest

    ncfilepath : str
        A filepath in the form of a string that points to the location
        of the netCDF file of interest

    offset : list
        Contains the lattitude and longitude offest in the form of
        [lat, lon]


    Returns
    -------
    Dictionary containing lat/lon, distance to, and corresponding x/y
    indices in the netCDF file (climate data) to the weather station
    that is closest to the input site_loc


    """

    data_dict = parse_data_orig(ncfilepath, offset)
    data_dict_flat = {i:j.flatten() for i,j in data_dict.items()}
    data_df = pd.DataFrame(data_dict_flat)

    data_df['coords'] = list(zip(data_df['lat'], data_df['lon']))

    my_dist = data_df['coords'].apply(lambda x: great_circle(x, site_loc).km)
    dist_min_idx = my_dist.idxmin()
    close_loc_nc = data_df.iloc[dist_min_idx,:]['coords']

    nc_ind = np.where(
        (data_dict['lat']==close_loc_nc[0]) &
        (data_dict['lon']==close_loc_nc[1]))

    out = {
             'ws_lat': close_loc_nc[0],
             'ws_lon': close_loc_nc[1],
             'dist': my_dist[dist_min_idx],
             'nc_xindex': nc_ind[1][0],
             'nc_yindex': nc_ind[0][0],
    }
    return out

def weather_data_calcs(nc_filepath, wstat_indices, ncwvar):
    """
    Extracts the weather and time data from a .nc file (nc_filepath)
    for specified location(wstat_coords)

    Parameters
    ----------
    ncfilepath : str
        A filepath in the form of a string that points to the location
        of the netCDF file of interest

    wstat_indices : tuple
        xc and yc indices corresponding to specified location
        (weather station of interest) in the form of (xc,yc)

    ncwvar : str
        Weather variable of interest to be extracted from you .nc file
        (e.g., 'pr', 'uas', or 'vas')


    Returns
    -------
    time_data : Numpy array
        Numpy array corresponding to time data

    weather_data: Numpy array
        Numpy array corresponding to weather data

    """

    nc_file = nc.Dataset(nc_filepath)
    nc_weather = nc_file.variables[ncwvar][:]
    my_xc = wstat_indices[0]
    my_yc = wstat_indices[1]
    weather_data = nc_weather[:, my_yc, my_xc]
    weather_data = np.ma.getdata(weather_data)
    time_data = nc_file.variables['time'][:]
    time_data = nc.ma.getdata(time_data)
    return time_data, weather_data

def make_ordered_time_weather_lists(nc_files, wstat_indices, ncwvar):
    """
    Takes a list of .nc files corresponding to different time frames
    for a specific weather model and produces an ordered list of time
    and weather numpy arrays for an identified weather station location
    (wstat_loc)

    Parameters
    ----------
    nc_files : list
        A list of strings, where each string is a filepath that points
        to the locations of the netCDF files corresponding to different
        years of a climate model

    wstat_indices : tuple
        xc and yc indices corresponding to specified location
        (weather station of interest) in the form of (xc,yc)

    ncwvar : str
        Weather variable of interest to be extracted from you .nc file
        (e.g., 'pr', 'uas', or 'vas')


    Returns
    -------
    time_list : list
        List of numpy arrays corresponding to time data

    weather_list: list
        List of numpy arrays corresponding to weather data

    """
    nclen = len(nc_files)
    my_xc = wstat_indices[0]
    my_yc = wstat_indices[1]
    mymap = map(
        weather_data_calcs,
        nc_files,
        np.tile([my_xc, my_yc], (nclen,1)),
        np.repeat(ncwvar, nclen)
        )
    mymap_list = list(mymap)

    time_list = [j[0] for i,j in zip(range(nclen), mymap_list)]
    weather_list = [j[1] for i,j in zip(range(nclen), mymap_list)]

    return time_list, weather_list


def timedelta_to_continuous_w_weather(
        time_data_list,
        weather_data_list,
        wvar,
        start_time,
        start_time_format="%Y-%m-%d %H:%M:%S",
        td_unit='days'):

    """
    Takes a list of time and weather numpy arrays that correspond to a
    specific location from a single climate model. Concatenates the
    time and weather lists into a single pandas data frame with
    continuous time and weather data as two separate columns of the
    data frame.


    Parameters
    ----------
    time_data_list : list
        List of numpy arrays corresponding to time data for a specific
        climate model

    weather_data_list: list
        List of numpy arrays corresponding to weather data for a
        specific climate model

    wvar : str
        Column name given to weather variable of interest in weather
        data frame (e.g., 'precip', 'uas', or 'vas')

    start_time : str
        Time stamp corresponding to the start time of the arrays in
        time_data_list (e.g., '1968-01-01 00:00:00')

    start_time_format : str
        Format in which the start_time is input
        (Default is '%Y-%m-%d %H:%M:%S')

    td_unit : str
        Unit in which the arrays in time_data_list are provided
        (e.g., 'days')


    Returns
    -------
    Pandas DataFrame with continuous time and weather data as two
    separate columns of the data frame

    """

    all_times = pd.Series(dtype='datetime64[ns]')
    all_weather = np.array([])
    for i in range(len(time_data_list)):
        time_deltas = pd.to_timedelta(time_data_list[i], unit=td_unit)
        times_parsed = (
            datetime.datetime.strptime(start_time, start_time_format) +
            pd.Series(time_deltas)
            )
        all_times = pd.concat([all_times, times_parsed], ignore_index=True)

        all_weather = np.concatenate([all_weather, weather_data_list[i]])

    timeweather_df = pd.DataFrame({'time': all_times, wvar: all_weather})
    return timeweather_df

def convert_preciprate_to_mm(precip_df, tint, wvar):

    """
    Converts precipitation rate (in [kg/m^2 s]) to total depth (in mm)
    when time interval in between timestamps is provided



    Parameters
    ----------
    precip_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: time,
                  dtype: datetime64[ns],
                  description: time stamps
            Name: precip,
                  dtype: float64,
                  description: precipitation rate in (kg/m^2-s)

    tint : float
        Time interval in between the timestamps in precipDF

    wvar : str
        Name given to preciptation column in precipitation data frame

    Returns
    -------
    Pandas DataFrame similar to input but with precipitation rate
    converted to total depth in mm.  Time stamps with NaNs in
    precipitation column are dropped from the data frame.

    """


    precip_df_mm = precip_df.copy()
    precip_df_mm.loc[:,wvar] = (
        precip_df_mm.loc[:,wvar]
        * (tint * 3600)
        * (1/1000)
        * 1000
        )
    precip_df_mm = precip_df_mm.dropna(subset=wvar)
    return precip_df_mm

def convert_to_daily(w_df, tvar, aggfun):

    """
    Converts a weather data frame with hourly time stamps to daily time
    stamps based on a user defined aggregation method



    Parameters
    ----------
    w_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: time,
                  dtype: datetime64[ns],
                  description: time stamps
            Name: any weather variable,
                  dtype: float64,
                  description: can be either precipitation (in mm) or
                               wind speed (in m/s)

    tvar : str
        Name given to time column in weather data frame

    aggfun : string
        Aggregation function that is read in by the 'aggregate' method
        for pandas groupby objects (e.g., 'sum', 'mean', etc.)

    Returns
    -------
    Pandas DataFrame similar to input but with daily time intervals
    instead of more frequent time intervals (e.g., hourly)

    """

    w_df = w_df.copy()
    w_df.loc[:,'date'] = w_df.loc[:, tvar].dt.date

    w_df_daily = w_df.groupby(['date']).aggregate(aggfun, numeric_only=True)
    #DF_daily.drop(columns=tvar, inplace=True)
    w_df_daily.reset_index(inplace=True)
    return w_df_daily

def convert_to_mm_daily(precip_df, tint, tvar, wvar, aggfun):

    """
    Converts precipitation rate (in [kg/m^2 s]) to daily total depth
    (in mm) when time interval in between timestamps is provided



    Parameters
    ----------
    precip_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: time,
                  dtype: datetime64[ns],
                  description: time stamps
            Name: precip,
                  dtype: float64,
                  description: precipitation rate in (kg/m^2-s)

    tint : float
        Time interval in between the timestamps in precipDF

    tvar : str
        Name given to time column in weather data frame

    wvar : str
        Name given to preciptation column in precipitation data frame

    aggfun : string
        Aggregation function that is read in by the 'aggregate' method
        for pandas groupby objects (e.g., 'sum', 'mean', etc.)

    Returns
    -------
    Pandas DataFrame similar to input but with precipitation rate
    converted to daily total depth (in mm)

    """

    precip_df = convert_preciprate_to_mm(precip_df, tint, wvar)
    precip_df = convert_to_daily(precip_df, tvar, aggfun)
    return precip_df

def convert_uasvas_to_wind(uas_df, vas_df, ucol, vcol, tvar, wndvar):

    """
    Converts u and v (east/west and north/south) components of surface
    wind into wind speed (in m/s). Any time stamps that result in NaNs
    for the output wind speed column are dropped from the output data
    frame.



    Parameters
    ----------
    uas_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: time,
                  dtype: datetime64[ns],
                  description: time stamps
            Name: uas,
                  dtype: float64,
                  description: u-component of surface wind (in m/s)

    vas_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: time,
                  dtype: datetime64[ns],
                  description: time stamps
            Name: uas,
                  dtype: float64,
                  description: v-component of surface wind (in m/s)

    ucol : str
        Name given to wind column in uasDF

    ucol : str
        Name given to wind column in vasDF

    tvar : str
        Name given to time column in uasDF

    wndvar : str
        Name to be given to wind speed column in output data frame

    Returns
    -------
    Pandas DataFrame with u and v components of wind converted to wind
    speed (in m/s)

    """

    time = uas_df.loc[:, tvar]
    uas = uas_df.loc[:,ucol]
    vas = vas_df.loc[:,vcol]
    wind = np.sqrt(uas ** 2 + vas ** 2)
    wind_df = pd.concat([time.rename(tvar), wind.rename(wndvar)], axis=1)
    wind_df = wind_df.dropna(subset=wndvar)
    return wind_df

def summary_stat_fun(daily_df_current, daily_df_future, wmodel, site):

    """
    Takes in a pandas data frame for daily weather and outputs
    statstical summaries for that data set
    (min, max, mean, and std. dev.)



    Parameters
    ----------
    daily_df_current : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: date,
                  dtype: datetime.date object,
                  description: historical dates
            Name: precip or wind,
                  dtype: float64,
                  description: any daily weather parameter
                               (e.g., precipitation or wind)

    daily_df_future : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: date,
                  dtype: datetime.date object,
                  description: future dates
            Name: precip or wind,
                  dtype: float64,
                  description: any daily weather
                  parameter (e.g., precipitation or wind)
    wmodel : str
        Name for the climate model used for weather data sets

    site : str
        Name for the specific site whose weather being analyzed



    Returns
    -------
    pandas.DataFrames with statistical summaries
    (min, max, mean, and std. dev.)

    """


    daily_df_current = daily_df_current.copy()
    daily_df_future = daily_df_future.copy()
    daily_df_current.set_index('date', inplace=True)
    daily_df_future.set_index('date', inplace=True)

    summary_stats_current = pd.DataFrame(
            {'model':[wmodel],
             'time_period':['current'],
             'site_name':[site],
             'min':daily_df_current.min().values,
             'mean':daily_df_current.mean().values,
             'max':daily_df_current.max().values,
             'sd':daily_df_current.std().values},
        index=[0]
        )
    summary_stats_future = pd.DataFrame(
            {'model':[wmodel],
             'time_period':['future'],
             'site_name':[site],
             'min':daily_df_future.min().values,
             'mean':daily_df_future.mean().values,
             'max':daily_df_future.max().values,
             'sd':daily_df_future.std().values},
        index=[0]
        )
    return summary_stats_current, summary_stats_future

def get_annual_max(daily_df, max_dict_rename, wmodel, period):
    """
    Takes in a pandas data frame for daily weather and outputs annual
    maximum for the years covered in the input data. Function also
    renames new data frame columns to user-defined preference.



    Parameters
    ----------
    daily_df: pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: date,
                  dtype: datetime.date object,
                  description: historical dates
            Name: precip or wind,
                  dtype: float64,
                  description: any daily weather
                  parameter (e.g., precipitation or wind)

    max_dict_rename : dict
        Dictionary used to rename weather data column in output data
        frame so as to distinguish from input data (e.g., from 'precip'
        in dailyDF to 'MaxPrecip' in output data frame).

    wmodel : str
        Name for the climate model used for weather data sets

    period: str
        Name for time period being considered (e.g., 'current' or 'future')

    Returns
    -------
    pandas.DataFrames with annual maximum weather for years covered in
    input data

    """
    daily_df = daily_df.copy()
    daily_df['year'] = daily_df['date'].apply(lambda x: x.year)
    daily_df.drop(columns='date', inplace=True)
    annual_df = daily_df.groupby('year').max().reset_index()
    annual_df.rename(columns=max_dict_rename, inplace=True)
    annual_df['model'] = wmodel
    annual_df['period'] = period
    return annual_df

def myextremes(ann_df, rp_array, wvar, alpha=None):
    """
    Uses pyextremes to fit extreme (maximum annual) weather data to a
    generalized extreme value distribution (GEVD). The GEVD fit is then
    used to calculate return values for user-defined return period and
    user-defined confidence intervals. Takes the output of
    get_annual_max for annDF


    Parameters
    ----------
    ann_df : pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: year,
                  dtype: string, float, or int
                  description: historical dates
            Name: precip or wind,
                  dtype: float64,
                  description: any daily weather
                  parameter (e.g., precipitation or wind)

    rp_array : numpy.ndarray
        Numpy array with return periods for which return values should
        be calculated with pyextremes

    wvar : str
        Column name given to weather variable of interest in annDF
        (e.g., 'MaxPrecip', 'MaxWind', etc)

    alpha : float
        Width of confidence interval (0,1).  If None (default), return
        None for upper and lower confidence interval bounds.

    Returns
    -------
    pandas.DataFrame providing return values for user-requested return
    periods. Upper and lower confidence bounds are also output if
    alpha is non-zero.

    """


    ann_df = ann_df.copy()
    ann_df.index = pd.to_datetime(ann_df.year, format='%Y')
    ser = ann_df[wvar]


    extmod = pyextremes.EVA(ser)
    extmod.get_extremes(method='BM', block_size='365.2425D')
    extmod.fit_model()

    out = extmod.get_summary(
        return_period=rp_array,
        alpha=alpha,
        n_samples=1000
        )


    return out

def find_rl_location(future_df, rt_lv):
    """
    Finds a return period corresponding to a specified return level in
    a data frame of return-periods/return-levels as output by
    pyextremes


    Parameters
    ----------
    future_df : pandas.DataFrame
        Index:
            return periods
        Columns:
            Name: return value,
                  dtype: float64,
                  description: return values of specified return
                               period (index)
            Name: lower ci,
                  dtype: float64,
                  description: lower confidence interval for return
                               values of specified return period
                               (index)
            Name: upper ci,
                  dtype: float64,
                  description: lower confidence interval for return
                  values of specified return period (index)

    rt_lv : float
        Return level of interest for which a corresponding return
        period should be identified.

    Returns
    -------
    Return period in future_df that most closely approximates the
    specified return level

    """

    future_df = future_df.copy()
    rp_diff = future_df.loc[:, 'return value']-rt_lv #return period
    return_period = (abs(rp_diff)).idxmin() #future location
    return return_period

def combined_boxplots(plotDF, wflag, site_name, savedir):
    """
    Generates boxplots of weather data.  Takes in a pandas data frame for annual extreme weather as captured by
    multiple weather models.  Requires categorical column for weather model and
    for the data time period (i.e, whether the data is currently/historically
    measured, or if the data is predicted by a weather model). Function then
    generates a boxplot for the data in the input data frame, capturing the
    different models in the x-axis, and where the time period is captured by
    the plot hues.



    Parameters
    ----------
    plotDF: pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: model, dtype: string object, description: climate model names
            Name: period, dtype: string object, description: label for 'current'
                or 'future' time period since data frame has combined 'current'
                and 'future' data.
            Name: year, dtype: int, description: year for
            Name: MaxPrecip or MaxWind, dtype: float64, description: any
                annual-max weather parameter (e.g., precipitation or wind)

    wflag : str
        flag that determines wich weather variable is being plotted
        (i.e., 'precip' or 'wind')

    site_name : str
        Name of site being analyzed

    savedir : str
        Relative or absolute path of where to save generated boxplots

    Returns
    -------
    None

    """
    # "combined" = combined current and future
    #plot_df has both, current and future, data
    #do I want a columns dictionary????  Think about the workflow and how things end up

    if wflag == 'precip':
        plotcol = 'MaxPrecip'
        ylabel = 'precip (mm)'
        title = 'Annual max precip data: '+site_name

    elif wflag == 'wind':
        plotcol = 'MaxWind'
        ylabel = 'wind (m/s)'
        title = 'Annual max wind data: '+site_name


    myfigsize=(8,6)
    fig, ax = plt.subplots(figsize=myfigsize)
    # plot_df.plot(x='model', y='max_wind')
    #

    sns.boxplot(x=plotDF.model, y=plotDF[plotcol], hue=plotDF.period, ax=ax)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    savenm = site_name+'_boxplot.png'
    fig.savefig(os.path.join(savedir, savenm), dpi=300)


def line_plot(site_name, period, singleDF, wflag, savedir, hue=None):
    """
    Generates boxplots of weather data.  Takes in a pandas data frame for annual extreme weather as captured by
    multiple weather models.  Requires categorical column for weather model and
    for the data time period (i.e, whether the data is currently/historically
    measured, or if the data is predicted by a weather model). Function then
    generates a boxplot for the data in the input data frame, capturing the
    different models in the x-axis, and where the time period is captured by
    the plot hues.



    Parameters
    ----------
    site_name : str
        Name of site being analyzed

    period : str
        label for time period being analyzed (e.g., 'current' or 'future')

    singleDF: pandas.DataFrame
        Index:
            RangeIndex
        Columns:
            Name: model, dtype: string object, description: climate model names
            Name: period, dtype: string object, description: label for 'current'
                or 'future' time period since data frame has isolated 'current'
                or 'future' data.
            Name: year, dtype: int, description: year for
            Name: MaxPrecip or MaxWind, dtype: float64, description: any
                annual-max weather parameter (e.g., precipitation or wind)

    wflag : str
        flag that determines wich weather variable is being plotted
        (i.e., 'precip' or 'wind')

    savedir : str
        Relative or absolute path of where to save generated boxplots

    hue : str
        column name for the corresponding to the different models to generate
        line plots of different colors based on the different models considred

    Returns
    -------
    None

    """

    #site_name = site name
    #period = 'Current' or 'Future'
    #single_df has only current or only future data
    #wflag = weather variable = 'MaxWind' or 'MaxPrecip'
    #hue should be set equal to the 'model' when having a dataframe with multiple models

    myfigsize=(8,6)
    fig, ax = plt.subplots(figsize=myfigsize)
    #plot_df.plot(x='model', y='max_wind')
    if wflag=='wind':
        ylabel = 'wind (m/s)'
        title = period+'-period annual max wind: '+site_name
        plotcol = 'MaxWind'

    elif wflag=='precip':
        ylabel = 'precipitation (mm)'
        title = period+'-period annual max precipitation: '+site_name
        plotcol = 'MaxPrecip'

    if hue != None:
        #hue should usually be set to "model"
        sns.lineplot(data=singleDF, x='year', y=plotcol, hue=hue, ax=ax)
    else:
        sns.lineplot(data=singleDF, x='year', y=plotcol, ax=ax)

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    savenm = site_name+'_'+period+'_'+wflag+'.png'
    fig.savefig(os.path.join(savedir, savenm), dpi=300)

