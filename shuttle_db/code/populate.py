import argparse
import csv
import psycopg2
import os
import re
import time

saved_cnns = set()
company_ids_by_name = {}
provider_ids_by_name = {}
shuttle_ids_by_plate = {}

_CLEAN_NAME_REGEX = re.compile(r'[^a-zA-Z0-9 ]')

def _unicode_method(self):
    return "{}({})".format(
        self.__class__.__name__,
        ",".join("{}={}".format(k, v) for k, v in self.__dict__.items()))


def _clean_name(name):
    return _CLEAN_NAME_REGEX.sub('', name)

def gen_chunks(csv_reader, chunk_size=100):
    chunk = []
    for i, row in enumerate(csv_reader, start=1):
        chunk.append(row)
        if i % chunk_size == 0:
            yield chunk
            chunk = []
    yield chunk


class ShuttleCompany:

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def bulk_save(connection, companies):
        if not companies:
            return []
        cursor = connection.cursor()
        template = "INSERT INTO shuttle_companies (name) VALUES {} RETURNING id"
        inserts = []
        for company in companies:
            if company.id is not None:
                raise RuntimeError("IDs must be None for bulk insert")
            inserts.append("('{}')".format(company.name))
        query = template.format(", ".join(inserts))
        cursor.execute(query)
        ids_tuples = cursor.fetchall()
        ids = [t[0] for t in ids_tuples]
        for id, company in zip(ids, companies):
            company.id = id
        connection.commit()
        return ids


class TechProvider:

    def __init__(self, id, name):
        self.name = name
        self.id = id

    @staticmethod
    def bulk_save(connection, providers):
        if not providers:
            return []
        cursor = connection.cursor()
        template = "INSERT INTO providers (name) VALUES {} RETURNING id"
        inserts = []
        for provider in providers:
            if provider.id is not None:
                raise RuntimeError("IDs must be none for bulk insert")
            inserts.append("('{}')".format(provider.name))

        query = template.format(", ".join(inserts))
        cursor.execute(query)
        ids_tuples = cursor.fetchall()
        ids = [t[0] for t in ids_tuples]
        for id, provider in zip(ids, providers):
            provider.id = id
        connection.commit()
        return ids


class Shuttle:
    __unicode__ = _unicode_method

    def __init__(self,
                 vehicle_make,
                 vehicle_model,
                 vehicle_year,
                 vehicle_status,
                 vehicle_capacity,
                 vehicle_license_plate,
                 vehicle_length,
                 vehicle_weight,
                 fuel_type,
                 permit_issuance_date,
                 placard_issuance_date):
        self.id = None
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        self.vehicle_year = vehicle_year
        self.vehicle_status = vehicle_status
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_license_plate = vehicle_license_plate
        self.vehicle_length = vehicle_length
        self.vehicle_weight = vehicle_weight
        self.fuel_type = fuel_type
        self.permit_issuance_date = permit_issuance_date
        self.placard_issuance_date = placard_issuance_date

    @staticmethod
    def bulk_save(connection, shuttles):
        if not shuttles:
            return []
        cursor = connection.cursor()
        template = ('INSERT INTO shuttles (vehicle_make, vehicle_model, vehicle_year, '
                    'vehicle_status, vehicle_capacity, vehicle_license_plate, vehicle_length, '
                    'vehicle_weight, fuel_type, permit_issuance_date, placard_issuance_date) VALUES {} '
                    'RETURNING id')

        insert_tuples = []
        for shuttle in shuttles:
            insert_tuples.append((shuttle.vehicle_make,
                                  shuttle.vehicle_model,
                                  shuttle.vehicle_year,
                                  shuttle.vehicle_status,
                                  shuttle.vehicle_capacity,
                                  shuttle.vehicle_license_plate,
                                  shuttle.vehicle_length,
                                  shuttle.vehicle_weight,
                                  shuttle.fuel_type,
                                  ("DATE " + shuttle.permit_issuance_date
                                   if shuttle.permit_issuance_date else None),
                                  ("DATE " + shuttle.placard_issuance_date
                                   if shuttle.placard_issuance_date else None)))

        inserts = []
        for insert_tuple in insert_tuples:
            inserts.append("({})".format(", ".join("'{}'".format(f) if f is not None else "NULL" for f in insert_tuple)))

        cursor.execute(template.format(", ".join(inserts)))
        results = cursor.fetchall()
        ids = [res[0] for res in results]
        for id, shuttle in zip(ids, shuttles):
            shuttle.id = id
        connection.commit()
        return ids


class CNN:
    __unicode__ = _unicode_method

    def __init__(self, cnn, street, st_type, zip_code, accepted, jurisdiction,
                 neighborhood, layer, cnntext, streetname, classcode,
                 street_gc, streetna_1, oneway, st_length, geometry):
        self.cnn = cnn
        self.street = street
        self.st_type = st_type
        self.zip_code = zip_code
        self.accepted = accepted
        self.jurisdiction = jurisdiction
        self.neighborhood = neighborhood
        self.layer = layer
        self.cnntext = cnntext
        self.streetname = streetname
        self.classcode = classcode
        self.street_gc = street_gc
        self.streetna_1 = streetna_1
        self.oneway = oneway
        self.st_length = st_length
        self.geometry = geometry


    @staticmethod
    def bulk_save(conn, new_cnns):
        if not new_cnns:
            return
        template = ('INSERT INTO cnn (cnn, street, st_type, zip_code, accepted, '
                    'jurisdiction, neighborhood, layer, cnntext, streetname, '
                    'classcode, street_gc, streetna_1, oneway, st_length, geom) '
                    'VALUES {} RETURNING cnn')

        insert_tuples = []
        for cnn in new_cnns:
            insert_tuples.append((
                cnn.cnn,
                cnn.street,
                cnn.st_type,
                cnn.zip_code,
                cnn.accepted,
                cnn.jurisdiction,
                cnn.neighborhood,
                cnn.layer,
                cnn.cnntext,
                cnn.streetname,
                cnn.classcode,
                cnn.street_gc,
                cnn.streetna_1,
                cnn.oneway,
                cnn.st_length,
                cnn.geometry
            ))

        inserts = []
        for insert_tuple in insert_tuples:
            inserts.append("({})".format(", ".join("'{}'".format(f) if f is not None else "NULL" for f in insert_tuple)))

        cursor = conn.cursor()
        cursor.execute(template.format(", ".join(inserts)))
        results = cursor.fetchall()
        cnns = [res[0] for res in results]
        for cnn in cnns:
            saved_cnns.add(cnn)
        conn.commit()
        return cnns


def initialize_cnns(connection):
    cursor = connection.cursor()
    query = "SELECT cnn FROM cnn"
    cursor.execute(query)
    results = cursor.fetchall()
    for res in results:
        saved_cnns.add(res)


def initialize_tech_providers(connection):
    cursor = connection.cursor()
    query = "SELECT id, name FROM providers"
    cursor.execute(query)
    results = cursor.fetchall()
    for res in results:
        provider_ids_by_name[res[1]] = res[0]


def initialize_shuttle_companies(connection):
    cursor = connection.cursor()
    query = "SELECT id, name FROM shuttle_companies"
    cursor.execute(query)
    results = cursor.fetchall()
    for res in results:
        company_ids_by_name[res[1]] = res[0]


def initialize_shuttles(connection):
    cursor = connection.cursor()
    query = "SELECT id, vehicle_license_plate FROM shuttles"
    cursor.execute(query)
    results = cursor.fetchall()
    for res in results:
        shuttle_ids_by_plate[res[1]] = res[0]


def get_all_new_tech_providers(dict_reader):
    print("keys : {}".format(dict_reader.fieldnames))
    seen_names = set()
    providers = []
    for row in dict_reader:
        provider_name = row['TECH_PROVIDER_NAME']
        provider_name = _clean_name(provider_name)
        if provider_name not in provider_ids_by_name and provider_name not in seen_names:
            provider = TechProvider(id=None, name=provider_name)
            providers.append(provider)
            seen_names.add(provider_name)

    return providers


def get_all_new_shuttle_companies(dict_reader):
    seen_names = set()
    companies = []
    for row in dict_reader:
        company_name = row['SHUTTLE_COMPANY']
        company_name = _clean_name(company_name)
        if company_name not in company_ids_by_name and company_name not in seen_names:
            company = ShuttleCompany(id=None, name=company_name)
            companies.append(company)
            seen_names.add(company_name)

    return companies


def get_all_new_shuttles(dict_reader):
    seen_plates = set()
    shuttles = []
    for row in dict_reader:
        plate = row['LICENSE_PLATE_NUM']
        plate = _clean_name(plate)
        if plate not in shuttle_ids_by_plate and plate not in seen_plates:
            shuttle = Shuttle(
                vehicle_make=row['VEHICLE_MAKE'],
                vehicle_model=row['VEHICLE_MODEL'],
                vehicle_year=row['VEHICLE_YEAR'],
                vehicle_status=row['VEHICLE_STATUS'],
                vehicle_capacity=row['VEHICLE_CAPACITY'],
                vehicle_length=row['VEHICLE_LENGTH'],
                vehicle_weight=row['VEHICLE_WEIGHT'],
                vehicle_license_plate=row['VEHICLE_LICENSE_PLATE'],
                fuel_type=row['FUEL_TYPE'],
                permit_issuance_date=row['PERMIT_ISSUANCE_DATE'],
                placard_issuance_date=row['PLACARD_ISSUANCE_DATE']
            )
            shuttles.append(shuttle)
            seen_plates.add(plate)

    return shuttles


def get_all_new_cnns(dict_reader):
    seen_cnns = set()
    new_cnns = []
    for row in dict_reader:
        cnn = row['CNN']
        if cnn not in saved_cnns and cnn not in seen_cnns:
            cnn = CNN(
                cnn=int(row['CNN']),
                street=row['STREET'],
                st_type=row['ST_TYPE'],
                zip_code=row['ZIP_CODE'],
                accepted=True if row['ACCEPTED'] == 'Y' else False,
                jurisdiction=row['JURISDICTI'],
                neighborhood=row['NHOOD'],
                layer=row['LAYER'],
                cnntext=str(row['CNNTEXT']),
                streetname=row['STREETNAME'],
                classcode=row['CLASSCODE'],
                street_gc=row['STREET_GC'],
                streetna_1=row['STREETNA_1'],
                oneway=row['ONEWAY'],
                st_length=row['ST_LENGTH_'],
                geometry=row['GEOM']
            )
            new_cnns.append(cnn)

    return new_cnns


def load_location_data(connection, rows):
    template = ('INSERT INTO shuttle_locations '
                '(tech_provider_id, shuttle_company_id, shuttle_id, location, local_timestamp, cnn) '
                'VALUES {} ')

    insert_rows = []
    for row in rows:
        provider_id = provider_ids_by_name[row['TECH_PROVIDER_NAME']]
        shuttle_company_id = company_ids_by_name[row['SHUTTLE_COMPANY']]
        shuttle_id = shuttle_ids_by_plate[row['VEHICLE_LICENSE_PLATE']]
        local_timestamp = "to_timestamp('{}', 'dd-MON-YY HH12.MI.SS.US AM')".format(row['TIMESTAMPLOCAL'])
        point = 'POINT({}, {})'.format(row['LOCATION_LONGITUDE'], row['LOCATION_LATITUDE'])
        cnn_raw = row['CNN']
        cnn = int(cnn_raw) if cnn_raw else 'NULL'
        if cnn not in saved_cnns:
            cnn = 'NULL'
        insert_row = '({}, {}, {}, {}, {}, {})'.format(provider_id, shuttle_company_id,
                                                      shuttle_id, point, local_timestamp, cnn)
        insert_rows.append(insert_row)

    cursor = connection.cursor()
    query = template.format(", ".join(insert_rows))
    cursor.execute(query)
    connection.commit()


def populate_cnn_data(db_connection, csv_file):
    with open(csv_file) as f:
        initialize_cnns(conn)
        print("Found {} CNNs in DB".format(len(saved_cnns)))
        print("Loading new CNNs...")
        new_cnns = get_all_new_cnns(csv.DictReader(f))
        print("Found {} new CNNs".format(len(new_cnns)))
        CNN.bulk_save(db_connection, new_cnns)


def populate_shuttle_data(db_connection, csv_file):

    with open(csv_file) as f:
        initialize_tech_providers(db_connection)
        print("Found {} tech providers in DB".format(len(provider_ids_by_name)))
        print("Loading new tech providers...")
        providers = get_all_new_tech_providers(csv.DictReader(f))
        print("Found {} new tech providers".format(len(providers)))
        TechProvider.bulk_save(db_connection, providers)
        for provider in providers:
            provider_ids_by_name[provider.name] = provider.id
        print("Saved {} new tech providers".format(len(providers)))

        f.seek(0)
        initialize_shuttle_companies(db_connection)
        print("Found {} shuttle companies in DB".format(len(company_ids_by_name)))
        companies = get_all_new_shuttle_companies(csv.DictReader(f))
        print("Found {} new shuttle companies".format(len(companies)))
        ShuttleCompany.bulk_save(db_connection, companies)
        for company in companies:
            company_ids_by_name[company.name] = company.id
        print("Saved {} new shuttle companies".format(len(companies)))

        f.seek(0)
        initialize_shuttles(db_connection)
        print("Found {} shuttles in DB".format(len(shuttle_ids_by_plate)))
        shuttles = get_all_new_shuttles(csv.DictReader(f))
        print("Found {} new shuttles in data".format(len(shuttles)))
        Shuttle.bulk_save(db_connection, shuttles)
        for shuttle in shuttles:
            shuttle_ids_by_plate[shuttle.vehicle_license_plate] = shuttle.id
        print("Saved {} new shuttles".format(len(shuttles)))

        f.seek(0)
        print("Loading location data...")
        start_time = time.time()
        for chunk in gen_chunks(csv.DictReader(f)):
            print("Saving {} rows.".format(len(chunk)))
            load_location_data(db_connection, chunk)
        print("Done loading location data. Took {:.1f}".format(time.time() - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--shuttle_csv', default='/tmp/shuttle_three_days.csv')
    parser.add_argument('--cnn_csv', default='/tmp/cnn_dim.csv')
    parser.add_argument('--ip', default='localhost')
    parser.add_argument('--cnn', action='store_true')
    parser.add_argument('--shuttles', action='store_true')
    args = parser.parse_args()
    #try:
    #    username = os.environ['SHUTTLE_DB_USER']
    #except KeyError:
    #    username = input('DB Username: ').strip()
    username = os.environ.get('SHUTTLE_DB_USER')

    #try:
    #    password = os.environ['SHUTTLE_DB_PASSWORD']
    #except KeyError:
    #    password = input('DB Password: ').strip()
    password=os.environ.get('SHUTTLE_DB_PASSWORD')
    #conn = psycopg2.connect(host='localhost', user=username, password=password,
    conn = psycopg2.connect(host=args.ip, user=username, password=password,
                            database='shuttle_database')
    if args.cnn:
        populate_cnn_data(conn, args.cnn_csv)
    else:
        print('Skipping CNN population')
    if args.shuttles:
        populate_shuttle_data(conn, args.shuttle_csv)
    else:
        print('Skipping shuttle population')

