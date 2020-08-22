from sqlalchemy import create_engine
import pymysql
import pandas as pd
import math
import numpy as np

def load_data(table = "frames", server_string="root:123@127.0.0.1:3306/MAC_Frames" ):
    """ Load provided table from the provided mysql server
    """
    print("\nLoading Table: ", table)
    engine = create_engine('mysql+pymysql://%s'%server_string, echo=False)
    df = pd.read_sql_query("SELECT * FROM %s"%table, engine, index_col = 'id')
    print("Loaded Table with %d entries\n" % df.shape[0])
    return df

    
def remove_ten_min(df):
    """ Remove first ten minutes of each days recording
        It seems like the oscillation of the SDR changes in the first ten minutes pretty much
        Because of this those information are not very useful and can distort the results
    """
    day_in_sec = 86400
    ten_min = 600

    def find_bound_days():
        """ Find timestamp for begining first and end of last day
        """
        min_record_time = df['record_time'].min()
        max_record_time = df['record_time'].max()
        lower_bound = min_record_time - (min_record_time%day_in_sec)
        upper_bound = max_record_time + day_in_sec - (max_record_time%day_in_sec)
        return lower_bound, upper_bound

    first_day, last_day = find_bound_days()
    num_days = int((last_day-first_day)/day_in_sec)
    #Check if dataset is recorded over multiple day
    if num_days < 2:
        print("Warning: The argument --remove_ten_min only makes sense for datasets over multiple day")
        print("Skip deletion\n")
        return df

    for x in range(num_days):
        lower_bound = x * day_in_sec + first_day
        tmp = df[df['record_time'] > lower_bound]
        tmp = tmp[tmp['record_time'] < lower_bound+day_in_sec]
        lower_bound = tmp['record_time'].min() + ten_min
        df = df.drop(tmp[tmp['record_time'] < lower_bound].index)

    return df


def group_by_mac(df):
    """ Group data frame by sender MAC
        Remove frames corresponding to groups with less than 10 data points
    """
    for name, group in df.groupby(['sender_mac']):
        if group.shape[0] < 10:
            df = df.drop(group.index)
    return df.groupby(['sender_mac'])

def resample(mac_groups, time_period):
    ''' Resample groped dataset by given time period
        Calculate one representative data point for all data points in the given time period
    '''
    resampled_devices = {}
    for name, one_device in mac_groups:
        one_device.record_time = pd.to_datetime(one_device.record_time, unit='s')
        one_device.set_index('record_time', inplace=True)
        resampled_devices[name] = one_device.resample(time_period).mean()
    return resampled_devices