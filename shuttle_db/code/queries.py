import os
import pandas as pd
import psycopg2

def get_all_shuttles(connection):
    cursor = connection.cursor()
    query = 'SELECT id, vehicle_license_plate, vehicle_model, vehicle_make, vehicle_year FROM shuttles'
    cursor.execute(query)
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['ID', 'LICENSE_PLATE', 'MODEL', 'MAKE', 'YEAR']).set_index('ID')


def get_points_for_shuttle(connection, license_plate=''):
    cursor = connection.cursor()
    query = 'SELECT local_timestamp, location[0], location[1] FROM shuttle_locations l LEFT OUTER JOIN shuttles s ON l.shuttle_id=s.id WHERE s.vehicle_license_plate = (%s)'

    cursor.execute(query, (license_plate,))
    results = cursor.fetchall()
    return pd.DataFrame.from_records(results, columns=['time', 'lat', 'lng']).set_index('time')



if __name__ == '__main__':
    conn = psycopg2.connect(host='localhost',
                            user=os.environ.get('SHUTTLE_DB_USERNAME'),
                            password=os.environ.get('SHUTTLE_DB_PASSWORD'),
                            database='shuttle_database')

    print(get_all_shuttles(conn))
