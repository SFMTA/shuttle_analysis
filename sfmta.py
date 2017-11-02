def lat_long(df, lat='LATITUDE', long='LONGITUDE'):
    lat_long_list = []

    for _, row in df.iterrows():
        lat_long_tuple = (row[lat], row[long])
        lat_long_list.append(lat_long_tuple)

    return lat_long_list

def lat_long_by_plate(df, plate):
    cols = ['LOCATION_LATITUDE', 'LOCATION_LONGITUDE', 'TIMESTAMPLOCAL',
                'LICENSE_PLATE_NUM', 'SHUTTLE_COMPANY']
    
    search = df['LICENSE_PLATE_NUM'] == plate
    plate_df = df[search][cols]
    plate_df.sort_values(by='TIMESTAMPLOCAL', ascending=True, inplace=True)
    plate_df = lat_long(plate_df, lat='LOCATION_LATITUDE', long='LOCATION_LONGITUDE')
    return plate_df