/*
 BSDRadius is released under BSD license.
 Copyright (c) 2006, DATA TECH LABS
 All rights reserved. 
 
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met: 
 * Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer. 
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 
 * Neither the name of the DATA TECH LABS nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission. 
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/


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

/*
 * Sample tables for mod_sql BSDRadius server module
*/
--- End user data should be stored here ---
CREATE TABLE users (
  userId serial,
  name varchar(100) NOT NULL,
  password varchar(100) NOT NULL default '',
  PRIMARY KEY (userId)
);

--- list of current calls ---
CREATE TABLE calls (
  callId serial,
  name varchar(100) NOT NULL,
  calling_num varchar(100) NOT NULL default '',
  called_num varchar(100) NOT NULL default '',
  call_duration integer NOT NULL default 0,
  h323confid varchar(35) NOT NULL,
  PRIMARY KEY (callId)
);

--- call detail records ---
CREATE TABLE cdr (
  callId serial,
  name varchar(100) NOT NULL,
  setup_time timestamp,
  start_time timestamp,
  end_time timestamp,
  calling_num varchar(100) NOT NULL default '',
  called_num varchar(100) NOT NULL default '',
  h323confid varchar(35) NOT NULL,
  PRIMARY KEY (callId)
);

/*
 * Create trigger which removes call entry from active calls table
 * after inserting call data in cdr table.
 */
 --- create plpgsql language handler ---
CREATE OR REPLACE FUNCTION plpgsql_call_handler() RETURNS language_handler AS
  '$libdir/plpgsql', 'plpgsql_call_handler'
LANGUAGE 'c' VOLATILE;
--- create plpgsql language validator ---
CREATE OR REPLACE FUNCTION plpgsql_validator(oid) RETURNS void AS
  '$libdir/plpgsql', 'plpgsql_validator'
LANGUAGE 'c' VOLATILE;
--- change function owner to pgsql ---
ALTER FUNCTION plpgsql_validator(oid) OWNER TO pgsql;
ALTER FUNCTION plpgsql_call_handler() OWNER TO pgsql;
--- create and load plpgsql language ---
CREATE TRUSTED LANGUAGE 'plpgsql' HANDLER plpgsql_call_handler
  VALIDATOR plpgsql_validator;

--- create trigger  function ---
CREATE OR REPLACE FUNCTION rm_finished_call() RETURNS trigger AS $$
BEGIN
  DELETE FROM calls WHERE h323confid = NEW.h323confid;
  RETURN NEW;
END
$$ LANGUAGE 'plpgsql' VOLATILE;
  
--- create trigger on cdr table ---
CREATE TRIGGER t_rm_finished_call AFTER INSERT ON cdr FOR EACH ROW
  EXECUTE PROCEDURE rm_finished_call();
