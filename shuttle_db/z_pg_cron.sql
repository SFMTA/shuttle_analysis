SELECT pg_sleep(10);
\c shuttle_database;
SELECT current_database();
CREATE EXTENSION IF NOT EXISTS pg_cron CASCADE;
