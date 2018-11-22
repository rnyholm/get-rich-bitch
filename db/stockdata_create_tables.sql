CREATE TABLE `markets` (
  `market` varchar(25) NOT NULL,
  PRIMARY KEY (`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `stocks` (
  `ticker` varchar(25) NOT NULL,
  `market` varchar(25) NOT NULL,
  `marketcap` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ticker`),
  KEY `fk_stocks_markets` (`market`),
  CONSTRAINT `fk_stocks_markets` FOREIGN KEY (`market`) REFERENCES `markets` (`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `prices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ticker` varchar(25) NOT NULL,
  `date` datetime DEFAULT NULL,
  `previousclose` decimal(6,4) DEFAULT NULL,
  `open` decimal(6,4) DEFAULT NULL,
  `daytrend` varchar(350) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_prices_stocks` (`ticker`),
  CONSTRAINT `fk_prices_stocks` FOREIGN KEY (`ticker`) REFERENCES `stocks` (`ticker`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

CREATE TABLE `indices` (
  `index` varchar(25) NOT NULL,
  `market` varchar(25) NOT NULL,
  `date` datetime DEFAULT NULL,
  `previousclose` decimal(6,4) DEFAULT NULL,
  `open` decimal(6,4) DEFAULT NULL,
  `daytrend` varchar(350) DEFAULT NULL,
  PRIMARY KEY (`index`),
  KEY `fk_indices_markets` (`market`),
  CONSTRAINT `fk_indices_markets` FOREIGN KEY (`market`) REFERENCES `markets` (`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
