import csv
import psycopg2
import time
import os

# CSV_FILENAME = 'C:\\Users\\traveler\\Downloads\\shuttle_three_days.csv'
CSV_FILENAME = 'C:\\Users\\traveler\\PycharmProjects\\shuttle_analysis\\fiftypoints.csv'

company_ids_by_name = {}
provider_ids_by_name = {}
shuttle_ids_by_plate = {}


def _unicode_method(self):
    return "{}({})".format(
        self.__class__.__name__,
        ",".join("{}={}".format(k, v) for k, v in self.__dict__.items()))


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
        print("executing: {}".format(query))
        cursor.execute(query)
        ids_tuples = cursor.fetchall()
        ids = [t[0] for t in ids_tuples]
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
        print('executing: {}'.format(query))
        cursor.execute(query)
        ids_tuples = cursor.fetchall()
        ids = [t[0] for t in ids_tuples]
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

        print(inserts)
        cursor.execute(template.format(", ".join(inserts)))
        results = cursor.fetchall()
        ids = [res[0] for res in results]
        connection.commit()
        return ids


class CNN:
    __unicode__ = _unicode_method

    def __init__(self,
                 street,
                 st_type,
                 zip_code,
                 accepted,
                 jurisdiction,
                 neighborhood,
                 layer,
                 cnntext,
                 streetname,
                 classcode,
                 street_gc,
                 streetna_1,
                 oneway,
                 st_length,
                 block_addrange,
                 block_location,
                 theorder,
                 corridor,
                 geometry):
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
        self.block_addrange = block_addrange
        self.block_location = block_location
        self.theorder = theorder
        self.corridor = corridor
        self.geometry = geometry


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
    seen_names = set()
    providers = []
    for row in dict_reader:
        provider_name = row['TECH_PROVIDER_NAME']
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


def load_location_data(dict_reader):
    for row in dict_reader:
        provider_id = provider_ids_by_name[row['TECH_PROVIDER_NAME']]
        shuttle_company_id = company_ids_by_name[row['SHUTTLE_COMPANY']]
        shuttle_id = shuttle_ids_by_plate[row['VEHICLE_LICENSE_PLATE']]


if __name__ == '__main__':
    try:
        username = os.environ['SHUTTLE_DB_USER']
    except KeyError:
        username = input('DB Username: ').strip()

    try:
        password = os.environ['SHUTTLE_DB_PASSWORD']
    except KeyError:
        password = input('DB Password: ').strip()

    conn = psycopg2.connect(host='localhost', user=username, password=password, database='shuttle_database')
    with open(CSV_FILENAME) as f:
        initialize_tech_providers(conn)
        print("Found {} tech providers in DB".format(len(provider_ids_by_name)))
        print("Loading new tech providers...")
        providers = get_all_new_tech_providers(csv.DictReader(f))
        for provider in providers:
            provider_ids_by_name[provider.name] = provider.id
        print("Found {} new tech providers".format(len(providers)))
        TechProvider.bulk_save(conn, providers)
        print("Saved {} new tech providers".format(len(providers)))

        f.seek(0)
        initialize_shuttle_companies(conn)
        print("Found {} shuttle companies in DB".format(len(company_ids_by_name)))
        companies = get_all_new_shuttle_companies(csv.DictReader(f))
        for company in companies:
            company_ids_by_name[company.name] = company.id
        print("Found {} new shuttle companies".format(len(companies)))
        ShuttleCompany.bulk_save(conn, companies)
        print("Saved {} new shuttle companies".format(len(companies)))

        f.seek(0)
        initialize_shuttles(conn)
        print("Found {} shuttles in DB".format(len(shuttle_ids_by_plate)))
        shuttles = get_all_new_shuttles(csv.DictReader(f))
        print("Found {} shuttles".format(len(shuttles)))
        Shuttle.bulk_save(conn, shuttles)
        print("Saved {} new shuttles".format(len(shuttles)))

        f.seek(0)
        print("Loading location data...")
        load_location_data(csv.DictReader(f))
