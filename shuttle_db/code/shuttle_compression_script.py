# coding: utf-8

# ## Step 1: Connect to the database and read the values

# In[17]:


import pandas as pd
from sqlalchemy import create_engine
import functools

def read_df_from_sql():
    engine = create_engine('postgresql://postgres@localhost/shuttle_database')

    conn = engine.connect()
    input_df = pd.read_sql("SELECT * FROM shuttle_locations LIMIT 1000", conn)
    return input_df


# ## Step 2: fill in the blanks on data that does not have CNN information

# In[34]:


def start_time(series):
    return functools.reduce(lambda x, y: x if x < y else y, series)


def new_cnn(series):
    if len(series) < 2:
        return True
    else:
        return series[0] != series[1]


def flatten_aggregations(df):
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df


def create_cnn_events(df):
    return df['cnn'].rolling(2, min_periods=1).apply(new_cnn).cumsum()


def to_summary_format(df):
    return pd.concat([
        df['shuttle_id first'],
        df['cnn first'],
        df['ts min'],
        df['ts max'],
        df['ts count']],
        axis=1,
        keys=['shuttle_id', 'cnn', 'start_time', 'end_time', 'num_points'])


def aggregate_by_cnn_event(df):
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
        sorted_df['cnn'].fillna(method='ffill', inplace=True)
        print(sorted_df)
        sorted_df['cnn_event'] = create_cnn_events(sorted_df)
        shuttle_map[name] = aggregate_by_cnn_event(sorted_df)

    return shuttle_map


# ## Step 4: Insert into shuttle_summary_facts Table
def write_summary_map(result):
    for a in result.values():
       a.to_sql(name='shuttle_summary_facts', index=False, if_exists='append',
                chunksize=10000, con=conn)

if __name__ == "__main__":
    df = read_df_from_sql()
    summaries = prep_df_for_summary(df)
    write_summary_map(summaries)
