CREATE DATABASE shuttle_database;
SELECT current_database();
\c shuttle_database;
SELECT current_database();
CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
/*CREATE EXTENSION IF NOT EXISTS pg_cron CASCADE;*/


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

DROP TABLE IF EXISTS cnn CASCADE;
CREATE TABLE IF NOT EXISTS "cnn" (
  cnn INTEGER PRIMARY KEY,
  street VARCHAR(256),
  st_type VARCHAR(20),
  zip_code CHAR(5),
  accepted BOOL,
  jurisdiction VARCHAR(20),
  neighborhood VARCHAR(256),
  layer VARCHAR(20),
  cnntext VARCHAR(20),
  streetname VARCHAR(256),
  classcode VARCHAR(20),
  street_gc VARCHAR(256),
  streetna_1 VARCHAR(256),
  oneway CHAR(1),
  st_length INTEGER,
  geom GEOMETRY(LINESTRING)
);



DROP TABLE IF EXISTS shuttle_locations CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_locations (
    shuttle_id INTEGER REFERENCES shuttles (id),
    tech_provider_id INTEGER REFERENCES providers (id),
    shuttle_company_id INTEGER REFERENCES shuttle_companies (id),
    local_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    location POINT,
    cnn INTEGER REFERENCES cnn (cnn)
);


DROP TABLE IF EXISTS shuttle_summary_facts CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_summary_facts (
    cnn_event_id INTEGER,
    shuttle_id VARCHAR(20),
    local_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    cnn INTEGER,
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
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


DROP TABLE IF EXISTS shuttle_stop_dim CASCADE;
CREATE TABLE IF NOT EXISTS shuttle_stop_dim (
	id SERIAL PRIMARY KEY,
	cnn_id INTEGER REFERENCES cnn (cnn),
	stop_location GEOMETRY(POINT),
  registration_expiration_date DATE
);

DROP TABLE IF EXISTS day_info_dim CASCADE;
CREATE TABLE IF NOT EXISTS day_info_dim (
    date_key DATE PRIMARY KEY,
    transit_holiday VARCHAR(20),
    weekday VARCHAR(20)
);








CREATE TABLE IF NOT EXISTS shuttle_locations (
    shuttle_id INTEGER REFERENCES shuttles (id),
    tech_provider_id INTEGER REFERENCES providers (id),
    shuttle_company_id INTEGER REFERENCES shuttle_companies (id),
    local_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    location POINT,
    cnn INTEGER REFERENCES cnn (cnn)
);


-- determines whether two TIMESTAMPs are within 15 minutes of eachother
CREATE OR REPLACE FUNCTION withinFifteenMinutes(local_timestamp TIMESTAMP, last_timestamp TIMESTAMP)
RETURNS boolean
    AS $$

    SELECT local_timestamp  < last_timestamp + 15 * interval '1 minute'

    $$
    LANGUAGE SQL
    IMMUTABLE
    PARALLEL SAFE
    RETURNS NULL ON NULL INPUT;


-- This function determines whether a point is a "new start". If there has been another point <15 minutes before,
-- it's still part of the same aggregation
CREATE OR REPLACE FUNCTION findNewStart(local_timestamp TIMESTAMP, last_timestamp TIMESTAMP )
RETURNS timestamp without time zone
    AS $$

    SELECT
        CASE
            WHEN last_timestamp IS NULL THEN local_timestamp
            ELSE
                CASE
                    WHEN NOT withinFifteenMinutes(local_timestamp, last_timestamp) THEN local_timestamp
                    ELSE NULL
            END
        END
    AS new_start

    $$
    LANGUAGE SQL
    IMMUTABLE;

-- this windowing function creates a column in each value that shows the last known point for that shuttle
-- sorted by timestamp
CREATE OR REPLACE FUNCTION windowByTimeStamps(start_time TIMESTAMP, end_time TIMESTAMP)
RETURNS TABLE( shuttle_id INTEGER ,
    tech_provider_id INTEGER ,
    shuttle_company_id INTEGER ,
    local_timestamp TIMESTAMP WITHOUT TIME ZONE,
    location POINT,
    cnn INTEGER ,
    last_timestamp timestamp without time zone)
    AS $$

    SELECT shuttle_locations.*, lag(local_timestamp) OVER (PARTITION BY shuttle_id ORDER BY local_timestamp) AS last_timestamp
    FROM shuttle_locations
    WHERE start_time < local_timestamp AND end_time > local_timestamp

    $$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;


-- determines the start times for each CNN "session". A session is a period of time in a CNN that is
-- < 15 minutes before the last time it was on that CNN
CREATE OR REPLACE FUNCTION groupCNNEvents(start_time TIMESTAMP, end_time TIMESTAMP)
RETURNS TABLE(
    shuttle_id INTEGER ,
    tech_provider_id INTEGER ,
    shuttle_company_id INTEGER ,
    local_timestamp TIMESTAMP WITHOUT TIME ZONE,
    location POINT,
    cnn INTEGER ,
    last_timestamp timestamp without time zone,
    start_time TIMESTAMP WITHOUT TIME ZONE
    )
    AS $$

    SELECT *, MAX(findNewStart(local_timestamp, last_timestamp)) OVER (PARTITION BY shuttle_id ORDER BY local_timestamp) as start_time
    FROM (
        SELECT * FROM windowByTimeStamps(start_time, end_time) s1
    ) s2

    $$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;




CREATE OR REPLACE FUNCTION cnnAggregation(s_time TIMESTAMP, e_time TIMESTAMP)
RETURNS TABLE(
    shuttle_id INTEGER ,
    tech_provider_id INTEGER ,
    shuttle_company_id INTEGER ,
    start_time TIMESTAMP WITHOUT TIME ZONE,
    end_time TIMESTAMP WITHOUT TIME ZONE,
    num_datapoints bigint
    )
     AS $$

    SELECT shuttle_id,
       tech_provider_id,
       shuttle_company_id,
       start_time,
       max(local_timestamp)  as end_time ,
       COUNT(*) AS num_datapoints
    FROM (
        SELECT * FROM groupCNNEvents(s_time, e_time )
    ) s1
    GROUP BY (shuttle_id, tech_provider_id, shuttle_company_id,  start_time)
    ORDER BY shuttle_id, start_time;

    $$
      LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;


CREATE OR REPLACE FUNCTION hourlyFunction(s_time TIMESTAMP, e_time TIMESTAMP)
RETURNS VOID
    AS $$
    INSERT INTO shuttle_summary_facts (SELECT * FROM cnnAggregation(s_time, e_time))
    $$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;



--CREATE FUNCTION aggregate_hour(TIMESTAMP, TIMESTAMP) RETURNS integer as $$
--
--BEGIN
--   SELECT count(*) into total FROM shuttle_locations;
--   RETURN total;
--END;

CREATE OR REPLACE FUNCTION findCNNGroup(start_time TIMESTAMP WITHOUT TIME ZONE,, end_time TIMESTAMP WITHOUT TIME ZONE,)
RETURNS TIMESTAMP WITHOUT TIME ZONE,
    AS $$ SELECT MAX(findNewStart(local_timestamp, last_timestamp)) OVER (PARTITION BY shuttle_id ORDER BY local_timestamp) as start_time
      FROM (SELECT * FROM windowByTimeStamps(start_time, end_time) s1 ) s2
      $$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;