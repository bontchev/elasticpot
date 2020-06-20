CREATE TABLE IF NOT EXISTS `connections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `sensor` int(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `time_idx` (`timestamp`),
  KEY `ip_idx` (`ip`),
  KEY `ip2_idx` (`timestamp`, `ip`)
);

CREATE TABLE IF NOT EXISTS `urls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `payloads` (
  `id` int(11) NOT NULL auto_increment,
  `input` varchar(3000) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
  `inputhash` varchar(66),
  PRIMARY KEY (`id`),
  UNIQUE (`inputhash`)
);

CREATE TABLE IF NOT EXISTS `user_agents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_agent` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `content_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `accept_languages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `accept_language` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `sensors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `geolocation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) DEFAULT NULL,
  `country_name` varchar(45) DEFAULT '',
  `country_iso_code` varchar(2) DEFAULT '',
  `city_name` varchar(128) DEFAULT '',
  `org` varchar(128) DEFAULT '',
  `org_asn` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE(`ip`)
);

