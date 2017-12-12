CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

DROP TABLE IF EXISTS "shuttle_facts";
CREATE TABLE "shuttle_facts"(
    SHUTTLE_ID varchar(20),
    LOCALTIMESTAMP TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    GPS_LOCATION geometry(POINT)
);

CREATE TABLE "shuttle_summary_facts"(
    CNN_EVENT_ID integer,
    SHUTTLE_ID varchar(20),
    LOCALTIMESTAMP TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CNN integer,
    STARTIME TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    ENDTIME TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    NUM_POINTS integer
);

SELECT create_hypertable('shuttle_facts', 'ts', 'shuttle_id', 2, create_default_indexes=>FALSE);
CREATE INDEX ON shuttle_facts (SHUTTLE_ID, LOCALTIMESTAMP desc);
CREATE INDEX ON shuttle_facts (LOCALTIMESTAMP desc, SHUTTLE_ID);
CREATE INDEX ON shuttle_facts (LOCALTIMESTAMP, GPS_LOCATION DESC);
CREATE INDEX ON shuttle_facts (GPS_LOCATION, LOCALTIMESTAMP desc);

SELECT SHUTTLE_ID, CNN, COUNT(*)
FROM "shuttle_facts"
WHERE LOCALTIMESTAMP < "2017/12/05 10:00:00"
OVER (
 PARTITION BY SHUTTLE_ID, 
 ORDER BY
 price
 )
;

CREATE TABLE "cnn_dim"(
	OBJECTID integer primary key,
	CNN integer,
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
	GEOM geometry(box)
);
CREATE INDEX ON cnn_dimGEOM, CNN);

CREATE TABLE "shuttle_dim"(
    SHUTTLE_ID varchar(20) primary key references shuttle_facts(SHUTTLE_ID),
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
    TECH_PROVIDER varchar(20),
);
CREATE INDEX ON shuttle_dim(TECH_PROVIDER, SHUTTLE_ID)

CREATE TABLE shuttle_stop_dim(
	STOP_ID integer  primary key,
	CNN integer,
	STOP_LOCATION geometry(POINT),
    REGISTRATION_EXPIRATION_DATE
)

CREATE TABLE day_info_dim(
    date_key date primary key,
    TRANSIT_HOLIDAY varchar(20),
    WEEKDAY varchar(20)
)
