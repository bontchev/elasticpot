CREATE TABLE IF NOT EXISTS `connections` (
  `id` INTEGER PRIMARY KEY,
  `timestamp` datetime DEFAULT NULL,
  `ip` varchar(15) DEFAULT NULL,
  `remote_port` int(11) DEFAULT NULL,
  `request` varchar(6) DEFAULT NULL,
  `url` int(4) DEFAULT NULL,
  `payload` int(4) DEFAULT NULL,
  `message` int(4) DEFAULT NULL,
  `user_agent` int(4) DEFAULT NULL,
  `content_type` int(4) DEFAULT NULL,
  `accept_language` int(4) DEFAULT NULL,
  `local_host` varchar(15) DEFAULT NULL,
  `local_port` int(11) DEFAULT NULL,
  `sensor` int(4) DEFAULT NULL
);

CREATE INDEX `time_idx` ON `connections` (`timestamp`);
CREATE INDEX `ip_idx` ON `connections` (`ip`);
CREATE INDEX `ip2_idx` ON `connections` (`timestamp`, `ip`);

CREATE TABLE IF NOT EXISTS `urls` (
  `id` INTEGER PRIMARY KEY,
  `path` varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `payloads` (
  `id` INTEGER PRIMARY KEY,
  `input` varchar(3000) NOT NULL,
  `inputhash` varchar(66),
  UNIQUE (`inputhash`)
);

CREATE TABLE IF NOT EXISTS `user_agents` (
  `id` INTEGER PRIMARY KEY,
  `user_agent` varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `content_types` (
  `id` INTEGER PRIMARY KEY,
  `content_type` varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `accept_languages` (
  `id` INTEGER PRIMARY KEY,
  `accept_language` varchar(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `messages` (
  `id` INTEGER PRIMARY KEY,
  `message` varchar(10) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `sensors` (
  `id` INTEGER PRIMARY KEY,
  `name` varchar(255) DEFAULT NULL,
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `geolocation` (
  `id` INTEGER PRIMARY KEY,
  `ip` varchar(15) DEFAULT NULL,
  `country_name` varchar(45) DEFAULT '',
  `country_iso_code` varchar(2) DEFAULT '',
  `city_name` varchar(128) DEFAULT '',
  `org` varchar(128) DEFAULT '',
  `org_asn` int(11) DEFAULT NULL,
  UNIQUE(`ip`)
);

