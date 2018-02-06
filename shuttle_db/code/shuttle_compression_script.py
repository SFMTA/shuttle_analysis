# coding: utf-8

# ## Step 1: Connect to the database and read the values

# In[17]:


import pandas as pd
from sqlalchemy import create_engine
import functools
import argparse

from datetime import timedelta
from dateutil import parser as dtparser

parser = argparse.ArgumentParser(description='populate summary table for timescale')
parser.add_argument('--backfill', dest='backfill', action='store_true',
                   help='are we running a backfill operation or not')
parser.add_argument('--hourly', dest='hourly', help='whether to perform an hourly update')

parser.add_argument('--start-date', dest='start_date',
                   help='start date for backfill')
parser.add_argument('--end-date', dest='end_date', help='end date for backfill')
parser.add_argument('--hour-to-process', dest='hour_to_process',
                    help='datetime formatted hour YYYY-MM-DD HH:00' )

engine = create_engine('postgresql://postgres@localhost/shuttle_database')
conn = engine.connect()


def read_timeframe_from_sql(start, end):

    """
    
    creates a dataframe given a start-time and end-time. can be used for hourly and
    backfill aggregations
    
    :param start: 
    :param end: 
    :return: 
    """
    query = "SELECT * FROM shuttle_locations WHERE "
    "local_timestamp > {start} and local_timestamp < {end}".format(start=start, end=end)

    input_df = pd.read_sql(query, conn)
    return input_df


def new_cnn(series):
    """
    Determines whether two data points take place in seperate CNNS or the same CNN.
    Will be used to split CNN events.

    :param series: 
    :return: 
    """
    if len(series) < 2:
        return True
    else:
        return series[0] != series[1]


def flatten_aggregations(df):
    """

    This is a "flatten" operation that will move aggregations (i.e. min, first, etc.)
    to the top level of the dataframe. These will later be stripped of their secondary
    names and turned into values that match rows in the shuttle_summary_facts table
    
    :param df: 
    :return: 
    """
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df


def create_cnn_events(df):
    """

    This function takes advantage of the cumsum() rolling window funtion to create
    individual cnn events.
    
    since new_cnn will return 1 for true, we can use cum_sum to turn an array of
    [0,1,0,0,1,0,1] -> [0,1,1,1,2,2,3]. This guarantees uniqueness if a shuttle ends
    up on the same CNN multiple times
    
    :param df: 
    :return: 
    """
    return df['cnn'].rolling(2, min_periods=1).apply(new_cnn).cumsum()


def to_summary_format(df):
    """

    changes aggregated results into a format that matches the shuttle_summary_facts table

    :param df: 
    :return: 
    """
    return pd.concat([
        df['shuttle_id first'],
        df['cnn first'],
        df['ts min'],
        df['ts max'],
        df['ts count']],
        axis=1,
        keys=['shuttle_id', 'cnn', 'start_time', 'end_time', 'num_points'])


def aggregate_by_cnn_event(df):
    """

    this function groups all values of the same 'cnn_event' together
    
    1. counts number of points
    2. finds start and end time
    3. returns a single row for each of these aggregations
    
    :param df: 
    :return: 
    """
    df['ts'] = df['local_timestamp'].astype('int64')
    df = df.groupby(['cnn_event'])
    df_agg = df.agg(
        {'shuttle_id': 'first', 'cnn': 'first', 'ts': ['min', 'max', 'count']})
    df_flat = flatten_aggregations(df_agg)
    res_df = to_summary_format(df_flat)
    res_df['start_time'] = pd.to_datetime(res_df['start_time'], unit='ns')
    res_df['end_time'] = pd.to_datetime(res_df['end_time'], unit='ns')
    return res_df


def prep_df_for_summary(df):
    dfs = df.groupby(['shuttle_id'])
    shuttle_map = {}
    for name, grouped in dfs:
        sorted_df = grouped.sort_values('local_timestamp')
        # this function assumes that if a CNN field is blank, it is a continuation of the
        # most recent cnn
        sorted_df['cnn'].fillna(method='ffill', inplace=True)
        sorted_df['cnn_event'] = create_cnn_events(sorted_df)
        shuttle_map[name] = aggregate_by_cnn_event(sorted_df)

    return shuttle_map


# ## Step 4: Insert into shuttle_summary_facts Table
def write_summary_map(result):
    """

    Writes all values to shuttle_summary_facts table
    
    :param result: 
    """
    for a in result.values():
       a.to_sql(name='shuttle_summary_facts', index=False, if_exists='append',
                chunksize=10000, con=conn)


def process(start_time, end_time):
    input_df = read_timeframe_from_sql(current_day, end_of_day)
    prepped = prep_df_for_summary(input_df)
    write_summary_map(prepped)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.backfill:
        print("performing backfill from {} to {}".format(args.start_date, args.end_date))
        start_date = dtparser.parse(args.start_date)
        end_date = dtparser.parse(args.end_date)
        delta = end_date - start_date

        num_days = delta.days

        for day in range(0,num_days):
            current_day = start_date + timedelta(day)
            end_of_day = current_day + timedelta(days=1)
            process(start_time=current_day, end_time=end_of_day)

    elif args.hourly:
        start_time = dtparser.parse(args.hour_to_process)
        end_time = start_time + timedelta(hours=1)
        process(start_time=start_time, end_time=end_time)

