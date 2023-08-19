CREATE TABLE IF NOT EXISTS
    urls (
        id serial PRIMARY KEY,
        name text,
        created_at timestamp
         );
CREATE INDEX IF NOT EXISTS name_idx ON urls(name);

CREATE TABLE IF NOT EXISTS
    url_checks (
        id serial PRIMARY KEY,
        url_id int references urls(id),
        status_code text,
        h1 text,
        title text,
        description text,
        created_at timestamp
               )