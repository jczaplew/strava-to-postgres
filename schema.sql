CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS activities (
    id serial primary key,
    source text,
    source_id bigint,
    name text,
    description text,
    activity text,
    start_time timestamp without time zone,
    moving_time bigint,
    elapsed_time bigint,
    distance numeric,
    elevation_gain numeric,
    average_speed numeric,
    max_speed numeric,
    gear_id text,
    trainer boolean,
    commute boolean,
    other jsonb,
    geom geometry(LineString, 4326)
);

CREATE INDEX IF NOT EXISTS activities_source_id_idx ON activities (source_id);
CREATE INDEX IF NOT EXISTS activities_activity_idx ON activities (activity);
CREATE INDEX IF NOT EXISTS activities_start_time_idx ON activities (start_time);
CREATE INDEX IF NOT EXISTS activities_gear_id_idx ON activities (gear_id);
CREATE INDEX IF NOT EXISTS activities_geom_idx ON activities USING GIST (geom);

CREATE TABLE IF NOT EXISTS gear (
    id serial primary key,
    source text,
    source_id text,
    name text,
    brand text,
    model text,
    description text
);

CREATE INDEX IF NOT EXISTS gear_source_id_id ON gear (source_id);
