CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

DROP TABLE IF EXISTS "shuttles" CASCADE;
CREATE TABLE IF NOT EXISTS "shuttles"(
  ID integer primary key,
  VEHICLE_MAKE varchar(20),
  VEHICLE_MODEL varchar(20),
  VEHICLE_YEAR varchar(20),
  VEHICLE_STATUS varchar(20),
  VEHICLE_CAPACITY varchar(20),
  VEHICLE_LICENSE_PLATE varchar(20),
  VEHICLE_LENGTH varchar(20),
  VEHICLE_WEIGHT varchar(20),
  FUEL_TYPE varchar(20),
  PERMIT_ISSUANCE_DATE date,
  PLACARD_ISSUANCE_DATE date,
  TECH_PROVIDER varchar(20)
);


DROP TABLE IF EXISTS shuttle_locations CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_locations (
    SHUTTLE_ID INTEGER REFERENCES shuttles (ID),
    LOCAL_TIMESTAMP TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    ROUTE geometry(LINESTRING),
    CNN integer REFERENCES cnn ( ID )
);


DROP TABLE IF EXISTS shuttle_summary_facts CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_summary_facts (
    CNN_EVENT_ID integer,
    SHUTTLE_ID varchar(20),
    LOCAL_TIMESTAMP TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CNN integer,
    STARTTIME TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    ENDTIME TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    NUM_POINTS integer
);

SELECT create_hypertable('shuttle_locations', 'local_timestamp', 'shuttle_id', 2, create_default_indexes=>FALSE);

SELECT SHUTTLE_ID, CNN, COUNT(*)
OVER (
 PARTITION BY SHUTTLE_ID
 ORDER BY shuttle_locations.LOCAL_TIMESTAMP
)
FROM shuttle_locations
WHERE LOCAL_TIMESTAMP < TIMESTAMP '2017/12/05 10:00:00';

DROP TABLE IF EXISTS cnn CASCADE;
CREATE TABLE IF NOT EXISTS "cnn" (
	ID integer PRIMARY KEY,
	STREET varchar(20),
	ST_TYPE varchar(20),
	ZIP_CODE char(5),
	ACCEPTED bool,
	JURISDICTI varchar(20),
	NHOOD varchar(20),
	LAYER varchar(20),
	CNNTEXT varchar(20),
	STREETNAME varchar(20),
	CLASSCODE varchar(20),
	STREET_GC varchar(20),
	STREETNA_1 varchar(20),
	ONEWAY bool,
	ST_LENGTH_ integer,
  BLOCK_ADDRANGE varchar(20),
  BLOCK_LOCATION varchar(20),
  THEORDER varchar(20),
  CORRIDOR varchar(20),
	GEOM geometry(POLYGON)
);

DROP TABLE IF EXISTS shuttle_stop_dim CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_stop_dim (
	STOP_ID integer  primary key,
	CNN integer,
	STOP_LOCATION geometry(POINT),
  REGISTRATION_EXPIRATION_DATE date
);

DROP TABLE IF EXISTS day_info_dim CASCADE;
CREATE TABLE IF NOT EXISTS day_info_dim (
    date_key date primary key,
    TRANSIT_HOLIDAY varchar(20),
    WEEKDAY varchar(20)
);
