CREATE TABLE IF NOT EXISTS connections (
  id SERIAL PRIMARY KEY,
  time_stamp timestamp DEFAULT NULL,
  ip varchar(15) DEFAULT NULL,
  remote_port integer DEFAULT NULL,
  request varchar(6) DEFAULT NULL,
  url smallint DEFAULT NULL,
  payload smallint DEFAULT NULL,
  message smallint DEFAULT NULL,
  user_agent smallint DEFAULT NULL,
  content_type smallint DEFAULT NULL,
  accept_language smallint DEFAULT NULL,
  local_host varchar(15) DEFAULT NULL,
  local_port integer DEFAULT NULL,
  sensor smallint DEFAULT NULL
);

CREATE INDEX time_idx ON connections (time_stamp);
CREATE INDEX ip_idx ON connections (ip);
CREATE INDEX ip2_idx ON connections (time_stamp, ip);

CREATE TABLE IF NOT EXISTS urls (
  id SERIAL PRIMARY KEY,
  path varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS payloads (
  id SERIAL PRIMARY KEY,
  input varchar(3000) NOT NULL,
  inputhash varchar(66)
);

CREATE UNIQUE INDEX hash_idx ON payloads (inputhash);

CREATE TABLE IF NOT EXISTS user_agents (
  id SERIAL PRIMARY KEY,
  user_agent varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS content_types (
  id SERIAL PRIMARY KEY,
  content_type varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS accept_languages (
  id SERIAL PRIMARY KEY,
  accept_language varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  message varchar(10) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS sensors (
  id SERIAL PRIMARY KEY,
  name varchar(255) DEFAULT NULL
);

CREATE UNIQUE INDEX name_idx ON sensors (name);

CREATE TABLE IF NOT EXISTS geolocation (
  id SERIAL PRIMARY KEY,
  ip varchar(15) DEFAULT NULL,
  country_name varchar(45) DEFAULT '',
  country_iso_code varchar(2) DEFAULT '',
  city_name varchar(128) DEFAULT '',
  org varchar(128) DEFAULT '',
  org_asn integer DEFAULT NULL
);

CREATE UNIQUE INDEX ip3_idx ON geolocation (ip);
