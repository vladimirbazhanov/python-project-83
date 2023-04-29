CREATE TABLE urls (id serial PRIMARY KEY, name text, created_at timestamp);
CREATE UNIQUE INDEX name_idx ON urls(name);