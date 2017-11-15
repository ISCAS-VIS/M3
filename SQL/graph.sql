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

