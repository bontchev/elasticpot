CREATE TABLE IF NOT EXISTS `connections` (
  `id` INTEGER PRIMARY KEY,
  `timestamp` DATETIME DEFAULT NULL,
  `ip` VARCHAR(15) DEFAULT NULL,
  `remote_port` INT(11) DEFAULT NULL,
  `request` VARCHAR(6) DEFAULT NULL,
  `url` INT(4) DEFAULT NULL,
  `payload` INT(4) DEFAULT NULL,
  `message` INT(4) DEFAULT NULL,
  `user_agent` INT(4) DEFAULT NULL,
  `content_type` INT(4) DEFAULT NULL,
  `accept_language` INT(4) DEFAULT NULL,
  `local_host` VARCHAR(15) DEFAULT NULL,
  `local_port` INT(11) DEFAULT NULL,
  `sensor` INT(4) DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS `time_idx` ON `connections` (`timestamp`);
CREATE INDEX IF NOT EXISTS `ip_idx` ON `connections` (`ip`);
CREATE INDEX IF NOT EXISTS `ip2_idx` ON `connections` (`timestamp`, `ip`);

CREATE TABLE IF NOT EXISTS `urls` (
  `id` INTEGER PRIMARY KEY,
  `path` VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `payloads` (
  `id` INTEGER PRIMARY KEY,
  `input` VARCHAR(3000) NOT NULL,
  `inputhash` VARCHAR(66),
  UNIQUE (`inputhash`)
);

CREATE TABLE IF NOT EXISTS `user_agents` (
  `id` INTEGER PRIMARY KEY,
  `user_agent` VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `content_types` (
  `id` INTEGER PRIMARY KEY,
  `content_type` VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `accept_languages` (
  `id` INTEGER PRIMARY KEY,
  `accept_language` VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `messages` (
  `id` INTEGER PRIMARY KEY,
  `message` VARCHAR(10) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `sensors` (
  `id` INTEGER PRIMARY KEY,
  `name` VARCHAR(255) DEFAULT NULL,
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `geolocation` (
  `id` INTEGER PRIMARY KEY,
  `ip` VARCHAR(15) DEFAULT NULL,
  `country_name` VARCHAR(45) DEFAULT '',
  `country_iso_code` VARCHAR(2) DEFAULT '',
  `city_name` VARCHAR(128) DEFAULT '',
  `org` VARCHAR(128) DEFAULT '',
  `org_asn` INT(11) DEFAULT NULL,
  UNIQUE(`ip`)
);

