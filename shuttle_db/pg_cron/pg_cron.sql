DO $$
BEGIN
   IF current_database() <> current_setting('cron.database_name') THEN
      RAISE EXCEPTION 'can only create extension in database %',
                      current_setting('cron.database_name')
      USING DETAIL = 'Jobs must be scheduled from the database configured in '||
                     'cron.database_name, since the pg_cron background worker '||
                     'reads job descriptions from this database.',
            HINT = format('Add cron.database_name = ''%s'' in postgresql.conf '||
                          'to use the current database.', current_database());
   END IF;
END;
$$;

CREATE SCHEMA cron;
CREATE SEQUENCE cron.jobid_seq;

CREATE TABLE cron.job (
	jobid bigint primary key default nextval('cron.jobid_seq'),
	schedule text not null,
	command text not null,
	nodename text not null default 'localhost',
	nodeport int not null default inet_server_port(),
	database text not null default current_database(),
	username text not null default current_user
);
GRANT SELECT ON cron.job TO public;
ALTER TABLE cron.job ENABLE ROW LEVEL SECURITY;
CREATE POLICY cron_job_policy ON cron.job USING (username = current_user);

CREATE FUNCTION cron.schedule(schedule text, command text)
    RETURNS bigint
    LANGUAGE C STRICT
    AS 'MODULE_PATHNAME', $$cron_schedule$$;
COMMENT ON FUNCTION cron.schedule(text,text)
    IS 'schedule a pg_cron job';

CREATE FUNCTION cron.unschedule(job_id bigint)
    RETURNS bool
    LANGUAGE C STRICT
    AS 'MODULE_PATHNAME', $$cron_unschedule$$;
COMMENT ON FUNCTION cron.unschedule(bigint)
    IS 'unschedule a pg_cron job';

CREATE FUNCTION cron.job_cache_invalidate()
    RETURNS trigger
    LANGUAGE C
    AS 'MODULE_PATHNAME', $$cron_job_cache_invalidate$$;
COMMENT ON FUNCTION cron.job_cache_invalidate()
    IS 'invalidate job cache';

CREATE TRIGGER cron_job_cache_invalidate
    AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
    ON cron.job
    FOR STATEMENT EXECUTE PROCEDURE cron.job_cache_invalidate();
