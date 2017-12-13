CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;


DROP TABLE IF EXISTS providers CASCADE;
CREATE TABLE IF NOT EXISTS providers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(256)
);

DROP TABLE IF EXISTS shuttle_companies CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(256)
);

DROP TABLE IF EXISTS shuttles CASCADE;
CREATE TABLE IF NOT EXISTS shuttles (
  id SERIAL PRIMARY KEY,
  vehicle_make VARCHAR(20),
  vehicle_model VARCHAR(20),
  vehicle_year VARCHAR(20),
  vehicle_status VARCHAR(20),
  vehicle_capacity VARCHAR(20),
  vehicle_license_plate VARCHAR(20),
  vehicle_length VARCHAR(20),
  vehicle_weight VARCHAR(20),
  fuel_type VARCHAR(20),
  permit_issuance_date DATE,
  placard_issuance_date DATE
);


DROP TABLE IF EXISTS shuttle_locations CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_locations (
    shuttle_id INTEGER REFERENCES shuttles (id),
    tech_provider_id INTEGER REFERENCES providers (id),
    shuttle_company_id INTEGER REFERENCES shuttle_companies (id),
    local_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    location POINT,
    cnn INTEGER REFERENCES cnn (id)
);


DROP TABLE IF EXISTS shuttle_summary_facts CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_summary_facts (
    cnn_event_id INTEGER,
    shuttle_id VARCHAR(20),
    local_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    cnn INTEGER,
    starttime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    endtime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    num_points INTEGER
);

SELECT CREATE_HYPERTABLE('shuttle_locations', 'local_timestamp', 'shuttle_id', 2, create_default_indexes=>FALSE);

SELECT shuttle_id, cnn, COUNT(*)
OVER (
 PARTITION BY shuttle_id
 ORDER BY shuttle_locations.local_timestamp
)
FROM shuttle_locations
WHERE local_timestamp < TIMESTAMP '2017/12/05 10:00:00';

DROP TABLE IF EXISTS cnn CASCADE;
CREATE TABLE IF NOT EXISTS "cnn" (
	id SERIAL PRIMARY KEY,
	street VARCHAR(20),
	st_type VARCHAR(20),
	zip_code CHAR(5),
	accepted BOOL,
	jurisdiction VARCHAR(20),
	neighborhood VARCHAR(20),
	layer VARCHAR(20),
	cnntext VARCHAR(20),
	streetname VARCHAR(20),
	classcode VARCHAR(20),
	street_gc VARCHAR(20),
	streetna_1 VARCHAR(20),
	oneway BOOL,
	st_length_ INTEGER,
  block_addrange VARCHAR(20),
  block_location VARCHAR(20),
  theorder VARCHAR(20),
  corridor VARCHAR(20),
	geom GEOMETRY(POLYGON)
);

DROP TABLE IF EXISTS shuttle_stop_dim CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_stop_dim (
	id SERIAL PRIMARY KEY,
	cnn_id INTEGER REFERENCES cnn (id),
	stop_location GEOMETRY(POINT),
  registration_expiration_date DATE
);

DROP TABLE IF EXISTS day_info_dim CASCADE;
CREATE TABLE IF NOT EXISTS day_info_dim (
    date_key DATE PRIMARY KEY,
    transit_holiday VARCHAR(20),
    weekday VARCHAR(20)
);