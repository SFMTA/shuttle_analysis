import os
import pandas as pd
import psycopg2

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


def get_points_for_shuttle(connection, license_plate=''):
    cursor = connection.cursor()
    query = '''SELECT local_timestamp, location[0], location[1] 
               FROM shuttle_locations l LEFT OUTER JOIN shuttles s 
               ON l.shuttle_id=s.id WHERE s.vehicle_license_plate = (%s)
               ORDER BY local_timestamp'''
    
    cursor.execute(query, (license_plate,))
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['time', 'lat', 'lng']).set_index('time')

def get_shuttles_companies(connection):
    cursor = connection.cursor()
    query = '''SELECT id, name 
               FROM shuttle_companies'''
    cursor.execute(query)
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['ID', 'NAME']).set_index('ID')


# def lat_long(df, lat='LATITUDE', long='LONGITUDE', time='TIMESTAMPLOCAL', cnn='CNN'):
#     lat_long_list = []

#     for _, row in df.iterrows():
#         lat_long_tuple = (row[lat], row[long], row[time], row[cnn])
#         lat_long_list.append(lat_long_tuple)

#     return lat_long_list

# def lat_long_by_plate(df, plate):
#     cols = ['LOCATION_LATITUDE', 'LOCATION_LONGITUDE', 'TIMESTAMPLOCAL',
#                 'LICENSE_PLATE_NUM', 'SHUTTLE_COMPANY', 'CNN']
    
#     search = df['LICENSE_PLATE_NUM'] == plate
#     plate_df = df[search][cols]
#     plate_df.sort_values(by='TIMESTAMPLOCAL', ascending=True, inplace=True)
#     plate_df = lat_long(plate_df, lat='LOCATION_LATITUDE', long='LOCATION_LONGITUDE')
#     return plate_df
