CREATE TABLE IF NOT EXISTS `user` (
   `ID` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
   `username` varchar(45) NOT NULL,
   `password` varchar(255),
   `salt` varchar(45),
   PRIMARY KEY (`ID`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8;