-- create nodes table
CREATE TABLE `stvis`.`nodes` ( `id` INT NOT NULL AUTO_INCREMENT , `nid` MEDIUMINT NOT NULL , `lat` DOUBLE NOT NULL , `lng` DOUBLE NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
-- nodes table index
ALTER TABLE `nodes` ADD INDEX( `lat`, `lng`);
ALTER TABLE `nodes` ADD INDEX( `rec_num`, `dev_num`);
ALTER TABLE `nodes` ADD INDEX( `seg`);
-- load data into table
LOAD DATA LOCAL INFILE "/enigma/tao.jiang/datasets/JingJinJi/records/bj-newvis/mares-at" INTO TABLE nodes COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5,@col6) set nid=@col1,lat=@col2,lng=@col3,dev_num=@col4,rec_num=@col5,seg=DATE_ADD("2016-07-05", INTERVAL @col6 HOUR);

-- create edges table
CREATE TABLE `stvis`.`edges` ( `id` INT NOT NULL AUTO_INCREMENT , `from_nid` INT NOT NULL , `to_nid` INT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
-- edges table index
ALTER TABLE `edges` ADD INDEX( `from_nid`, `to_nid`);
ALTER TABLE `edges` ADD INDEX( `rec_num`, `dev_num`);
ALTER TABLE `edges` ADD INDEX( `seg`);
-- load data into table
LOAD DATA LOCAL INFILE "/enigma/tao.jiang/datasets/JingJinJi/records/bj-newvis/rares-at" INTO TABLE edges COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5) set from_nid=@col1,to_nid=@col2,dev_num=@col3,rec_num=@col4,seg=DATE_ADD("2016-07-05", INTERVAL @col5 HOUR);

-- new matrix table
CREATE TABLE `stvis`.`matrixs` ( `id` INT NOT NULL AUTO_INCREMENT , `nid` INT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
ALTER TABLE `matrixs` ADD INDEX( `nid`, `seg`);
ALTER TABLE `matrixs` ADD INDEX( `rec_num`, `dev_num`);

-- abase 行政区划数据
CREATE TABLE `stvis`.`abase` ( `id` INT NOT NULL AUTO_INCREMENT , `nid` MEDIUMINT NOT NULL , `name` CHAR(10) NOT NULL , `lat` DOUBLE NOT NULL , `lng` DOUBLE NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
LOAD DATA LOCAL INFILE "/home/taojiang/git/statePrediction/datasets/beijingAdmin.csv" INTO TABLE abase COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4) set nid=@col1,name=@col2,lat=@col4,lng=@col3;

-- anode 行政区划点数据
CREATE TABLE `stvis`.`anode` ( `id` INT NOT NULL AUTO_INCREMENT , `nid` MEDIUMINT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
LOAD DATA LOCAL INFILE "/datahouse/tao.jiang/bj-newvis-sg/apoint-at" INTO TABLE anode COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5,@col6) set nid=@col1,dev_num=@col2,rec_num=@col3,seg=DATE_ADD("2016-07-05", INTERVAL @col4 HOUR);

-- aaedge 行政区划边数据
CREATE TABLE `stvis`.`aaedge` ( `id` INT NOT NULL AUTO_INCREMENT , `from_nid` INT NOT NULL , `to_nid` INT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
LOAD DATA LOCAL INFILE "/datahouse/tao.jiang/bj-newvis-sg/aaedge-at" INTO TABLE aaedge COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5,@col6,@col7) set from_nid=@col1,to_nid=@col2,dev_num=@col3,rec_num=@col4,seg=DATE_ADD("2016-07-05", INTERVAL @col5 HOUR);

-- v2
-- anodev2 点数据
CREATE TABLE `stvis`.`anodev2` ( `id` INT NOT NULL AUTO_INCREMENT , `nid` MEDIUMINT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
LOAD DATA LOCAL INFILE "/datahouse/tao.jiang/bj-newvis-sg/apoint-at" INTO TABLE anodev2 COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5,@col6) set nid=@col1,dev_num=@col2,rec_num=@col3,seg=DATE_ADD("2016-07-05", INTERVAL @col4 HOUR);

-- aaedgev2 行政区划边数据
CREATE TABLE `stvis`.`aaedgev2` ( `id` INT NOT NULL AUTO_INCREMENT , `from_nid` INT NOT NULL , `to_nid` INT NOT NULL , `rec_num` INT NOT NULL , `dev_num` INT NOT NULL , `seg` TIMESTAMP NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;
LOAD DATA LOCAL INFILE "/datahouse/tao.jiang/bj-newvis-sg/aaedge-at" INTO TABLE aaedgev2 COLUMNS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '"' LINES TERMINATED BY '\n' (@col1,@col2,@col3,@col4,@col5,@col6,@col7) set from_nid=@col1,to_nid=@col2,dev_num=@col3,rec_num=@col4,seg=DATE_ADD("2016-07-05", INTERVAL @col5 HOUR);
