
```
-- MySQL dump 10.9
--
-- Host: localhost    Database: bsdradius
-- ------------------------------------------------------
-- Server version	4.1.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `calls`
--

DROP TABLE IF EXISTS `calls`;
CREATE TABLE `calls` (
  `callId` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL default '',
  `calling_num` varchar(100) NOT NULL default '',
  `called_num` varchar(100) NOT NULL default '',
  `call_duration` int(11) unsigned NOT NULL default '0',
  `h323confid` varchar(35) NOT NULL default '',
  PRIMARY KEY  (`callId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `calls`
--


/*!40000 ALTER TABLE `calls` DISABLE KEYS */;
LOCK TABLES `calls` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `calls` ENABLE KEYS */;

--
-- Table structure for table `cdr`
--

DROP TABLE IF EXISTS `cdr`;
CREATE TABLE `cdr` (
  `callId` int(11) unsigned NOT NULL auto_increment,
  `userId` int(11) NOT NULL default '0',
  `setupTime` datetime default NULL,
  `startTime` datetime default NULL,
  `endTime` datetime default NULL,
  `callingNum` varchar(100) NOT NULL default '',
  `calledNum` varchar(100) NOT NULL default '',
  `h323confid` varchar(35) NOT NULL default '',
  `duration` int(11) NOT NULL default '0',
  `callingIp` varchar(20) NOT NULL default '255.255.255.255',
  `calledIp` varchar(20) NOT NULL default '255.255.255.255',
  PRIMARY KEY  (`callId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `cdr`
--


/*!40000 ALTER TABLE `cdr` DISABLE KEYS */;
LOCK TABLES `cdr` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `cdr` ENABLE KEYS */;

--
-- Table structure for table `destCodes`
--

DROP TABLE IF EXISTS `destCodes`;
CREATE TABLE `destCodes` (
  `destCodeId` int(11) NOT NULL auto_increment,
  `destCode` varchar(20) NOT NULL default '',
  `destinationId` int(11) NOT NULL default '0',
  PRIMARY KEY  (`destCodeId`),
  UNIQUE KEY `destCode` (`destCode`),
  KEY `destcodes_ibfk_1` (`destinationId`),
  CONSTRAINT `destcodes_ibfk_1` FOREIGN KEY (`destinationId`) REFERENCES `destinations` (`destinationId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `destCodes`
--


/*!40000 ALTER TABLE `destCodes` DISABLE KEYS */;
LOCK TABLES `destCodes` WRITE;
INSERT INTO `destCodes` VALUES (1,'44',1),(2,'447',2),(3,'7',3),(4,'7095',4);
UNLOCK TABLES;
/*!40000 ALTER TABLE `destCodes` ENABLE KEYS */;

--
-- Table structure for table `destinations`
--

DROP TABLE IF EXISTS `destinations`;
CREATE TABLE `destinations` (
  `destinationId` int(11) NOT NULL auto_increment,
  `destDescription` varchar(40) NOT NULL default '',
  PRIMARY KEY  (`destinationId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `destinations`
--


/*!40000 ALTER TABLE `destinations` DISABLE KEYS */;
LOCK TABLES `destinations` WRITE;
INSERT INTO `destinations` VALUES (1,'United Kingdom'),(2,'United Kingdom Mobile'),(3,'Russia'),(4,'Russia - Moscow');
UNLOCK TABLES;
/*!40000 ALTER TABLE `destinations` ENABLE KEYS */;

--
-- Table structure for table `radiusClients`
--

DROP TABLE IF EXISTS `radiusClients`;
CREATE TABLE `radiusClients` (
  `clientId` int(11) unsigned NOT NULL auto_increment,
  `address` varchar(100) NOT NULL default 'localhost',
  `name` varchar(100) NOT NULL default '',
  `secret` varchar(100) NOT NULL default '',
  PRIMARY KEY  (`clientId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `radiusClients`
--


/*!40000 ALTER TABLE `radiusClients` DISABLE KEYS */;
LOCK TABLES `radiusClients` WRITE;
INSERT INTO `radiusClients` VALUES (1,'127.0.0.1','gnugk','gktest123');
UNLOCK TABLES;
/*!40000 ALTER TABLE `radiusClients` ENABLE KEYS */;

--
-- Table structure for table `rateItems`
--

DROP TABLE IF EXISTS `rateItems`;
CREATE TABLE `rateItems` (
  `rateItemId` int(11) NOT NULL auto_increment,
  `ratePerCall` decimal(20,8) NOT NULL default '0.00000000',
  `ratePerMinute` decimal(20,8) NOT NULL default '0.00000000',
  `increment` int(4) NOT NULL default '1',
  `grace` int(4) NOT NULL default '0',
  `minDur` int(4) NOT NULL default '1',
  `rateTableId` int(11) NOT NULL default '0',
  `destinationId` int(11) NOT NULL default '0',
  `status` int(1) NOT NULL default '1',
  PRIMARY KEY  (`rateItemId`),
  UNIQUE KEY `table_dest` (`rateTableId`,`destinationId`),
  KEY `destinationId` (`destinationId`),
  CONSTRAINT `rateItems_ibfk_2` FOREIGN KEY (`rateTableId`) REFERENCES `rateTables` (`rateTableId`),
  CONSTRAINT `rateItems_ibfk_3` FOREIGN KEY (`destinationId`) REFERENCES `destinations` (`destinationId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `rateItems`
--


/*!40000 ALTER TABLE `rateItems` DISABLE KEYS */;
LOCK TABLES `rateItems` WRITE;
INSERT INTO `rateItems` VALUES (1,'0.01000000','0.19000000',1,0,1,1,1,1),(2,'0.01000000','0.09000000',1,0,1,1,2,1),(3,'0.01000000','0.12000000',1,0,1,1,3,1),(4,'0.00500000','0.15000000',60,6,60,1,4,1);
UNLOCK TABLES;
/*!40000 ALTER TABLE `rateItems` ENABLE KEYS */;

--
-- Table structure for table `rateTables`
--

DROP TABLE IF EXISTS `rateTables`;
CREATE TABLE `rateTables` (
  `rateTableId` int(11) NOT NULL auto_increment,
  `rateTableName` varchar(40) NOT NULL default '',
  PRIMARY KEY  (`rateTableId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `rateTables`
--


/*!40000 ALTER TABLE `rateTables` DISABLE KEYS */;
LOCK TABLES `rateTables` WRITE;
INSERT INTO `rateTables` VALUES (1,'default table');
UNLOCK TABLES;
/*!40000 ALTER TABLE `rateTables` ENABLE KEYS */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `userId` int(11) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL default '',
  `password` varchar(100) NOT NULL default '',
  `status` int(1) NOT NULL default '0',
  `rateTableId` int(11) NOT NULL default '0',
  `balance` decimal(20,8) NOT NULL default '0.00000000',
  PRIMARY KEY  (`userId`),
  KEY `rateTableId` (`rateTableId`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`rateTableId`) REFERENCES `rateTables` (`rateTableId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--


/*!40000 ALTER TABLE `users` DISABLE KEYS */;
LOCK TABLES `users` WRITE;
INSERT INTO `users` VALUES (1,'10001','10001',1,1,'10.00000000'),(2,'10002','10002',1,1,'10.00000000'),(3,'123458','123458',1,1,'10.00000000'),(4,'123459','123459',1,1,'10.00000000'),(5,'9999660099','9999660099',1,1,'20.00000000');
UNLOCK TABLES;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

```