import os
import psycopg2
import pandas as pd
from ipywidgets import Dropdown

def db_connect(url):
    try:
        username = os.environ['SHUTTLE_DB_USER']
    except KeyError:
        username = input('DB Username: ').strip()

    try:
        password = os.environ['SHUTTLE_DB_PASSWORD']
    except KeyError:
        password = input('DB Password: ').strip()

    conn = psycopg2.connect(host=url, 
                            user=username, 
                            password=password, 
                            database='shuttle_database')

    print('Connection Created')
    return conn

def get_all_shuttles(connection):
    cursor = connection.cursor()
    query = '''SELECT id, vehicle_license_plate, vehicle_model, vehicle_make, vehicle_year 
               FROM shuttles'''
    cursor.execute(query)
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['ID', 'LICENSE_PLATE', 
                                                       'MODEL', 'MAKE', 'YEAR']).set_index('ID')


def get_points_for_shuttle(connection, plate, start, end):
    cursor = connection.cursor()
    query = '''SELECT local_timestamp, location[0], location[1] 
               FROM shuttle_locations l LEFT OUTER JOIN shuttles s 
               ON l.shuttle_id=s.id WHERE s.vehicle_license_plate=%(plate)s
               AND local_timestamp BETWEEN %(start)s::timestamp
                 AND %(end)s::timestamp
               ORDER BY local_timestamp;'''

    cursor.execute(query, {'plate': plate, 'start':start, 'end':end,} )
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['time', 'lat', 'lng']).set_index('time')

def get_shuttles_companies(connection):
    cursor = connection.cursor()
    query = '''SELECT id, name 
               FROM shuttle_companies'''
    cursor.execute(query)
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['ID', 'NAME']).set_index('ID')