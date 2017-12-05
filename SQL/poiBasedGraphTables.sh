# grid table
 mongoimport --db stvis --collection grids --file grid-at.json  --jsonArray --numInsertionWorkers 8

# poi table
mongoimport --db stvis --collection pois --file mongo.json --jsonArray --numInsertionWorkers 8

# matrix table
mongoimport --db stvis --collection matrixs --file hares-jat.json  --jsonArray --numInsertionWorkers 8
