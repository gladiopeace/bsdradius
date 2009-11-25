--- Bsdradius database ---

/* 
 * Radius server client data is stored
 * in this table.
*/
CREATE TABLE radiusClients (
  clientId serial,
  address varchar(100) NOT NULL default 'localhost',
  name varchar(100) NOT NULL default '',
  secret varchar(100) NOT NULL,
  PRIMARY KEY (clientId)
);
