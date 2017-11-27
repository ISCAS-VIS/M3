# grid table
# [nid] [x] [y] [lat] [lng] [pid]
CREATE TABLE `stvis`.`grid` ( `nid` MEDIUMINT NOT NULL , `pid` CHAR(10) NOT NULL DEFAULT '0' , PRIMARY KEY (`nid`)) ENGINE = InnoDB;

# poi table
mongoimport --db stvis --collection pois --file mongo.json --jsonArray --numInsertionWorkers 8

# matrix table

