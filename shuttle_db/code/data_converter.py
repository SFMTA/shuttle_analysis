import pandas


def convert_raw_to_usable():
    print("reading")
    df = pandas.read_csv('./data_raw/shuttle_three_days.csv', sep='\t')
    cnn_df = pandas.read_csv('./data_raw/cnn_dim.csv', sep='\t')
    facts_df = df[['LICENSE_PLATE_NUM','TIMESTAMPLOCAL','LOCATION_LATITUDE','LOCATION_LONGITUDE']]

    facts_df['POINT'] = create_point(df)
    facts_df['LICENSE_PLATE_NUM'] = facts_df['LICENSE_PLATE_NUM']

    print("read")
    [print('\t' + x + ',') for x in cnn_df.columns.values]

    print([x for x in list(df.columns.values) if 'LOC' in x])
    print(facts_df.head(10))

    facts_df.to_csv('./data/shuttle_facts.csv',
                    columns=['LICENSE_PLATE_NUM','TIMESTAMPLOCAL','POINT'],
                    index=False)
    cnn_df.to_csv('./data/cnn_dim.csv',
                    index=False)






def create_point(df):
    return 'Point(' + \
           df['LOCATION_LATITUDE'].astype(str) + \
           ',' + \
           df['LOCATION_LONGITUDE'].astype(str) \
           + ')'


convert_raw_to_usable()

