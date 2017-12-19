import os
import pandas as pd
import psycopg2
import ipywidgets as widgets

def db_connect():
    try:
        username = os.environ['SHUTTLE_DB_USER']
    except KeyError:
        username = input('DB Username: ').strip()

    try:
        password = os.environ['SHUTTLE_DB_PASSWORD']
    except KeyError:
        password = input('DB Password: ').strip()

    conn = psycopg2.connect(host='localhost', 
                            user=username, 
                            password=password, 
                            database='shuttle_database')
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



################ Widgets ########################
def time_drop_down():
    values = {'12:00am': '00:00:00', '12:30am': '00:30:00', '1:00am': '01:00:00',
              '1:30am': '01:30:00', '2:00am': '02:00:00', '2:30am': '02:30:00',
              '3:00am': '03:00:00', '3:30am': '03:30:00', '4:00am': '04:00:00',
              '4:30am': '04:30:00', '5:00am': '05:00:00', '5:30am': '05:30:00',
              '6:00am': '06:00:00', '6:30am': '06:30:00', '7:00am': '07:00:00',
              '7:30am': '07:30:00', '8:00am': '08:00:00', '8:30am': '08:30:00',
              '9:00am': '09:00:00', '9:30am': '09:30:00', '10:00am': '10:00:00',
              '10:30am': '10:30:00', '11:00am': '11:00:00', '11:30am': '11:30:00',
              '12:00pm': '12:00:00', '12:30pm': '12:30:00', '1:00pm': '13:00:00',
              '1:30pm': '13:30:00', '2:00pm': '14:00:00', '2:30pm': '14:30:00',
              '3:00pm': '15:00:00', '3:30pm': '15:30:00', '4:00pm': '16:00:00',
              '4:30pm': '16:30:00', '5:00pm': '17:00:00', '5:30pm': '17:30:00',
              '6:00pm': '18:00:00', '6:30pm': '18:30:00', '7:00pm': '19:00:00',
              '7:30pm': '19:30:00', '8:00pm': '20:00:00', '8:30pm': '20:30:00',
              '9:00pm': '21:00:00', '9:30pm': '21:30:00', '10:00pm': '22:00:00',
              '10:30pm': '22:30:00', '11:00pm': '23:00:00', '11:30pm': '23:30:00'}
    dd = widgets.Dropdown(description='Time', options=values, value='07:00:00')
    return dd