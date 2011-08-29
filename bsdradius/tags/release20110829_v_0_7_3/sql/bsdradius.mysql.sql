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
CREATE TABLE IF NOT EXISTS radiusClients (
  clientId integer(11) unsigned auto_increment,
  address varchar(100) NOT NULL default 'localhost',
  name varchar(100) NOT NULL default '',
  secret varchar(100) NOT NULL,
  PRIMARY KEY (clientId)
);

CREATE TABLE IF NOT EXISTS users (
  userId integer(11) unsigned auto_increment,
  name varchar(100) NOT NULL,
  password varchar(100) NOT NULL default '',
  PRIMARY KEY (userId)
);

CREATE TABLE IF NOT EXISTS calls (
  callId integer(11) unsigned auto_increment,
  name varchar(100) NOT NULL,
  calling_num varchar(100) NOT NULL default '',
  called_num varchar(100) NOT NULL default '',
  call_duration integer(11) unsigned NOT NULL default 0,
  h323confid varchar(35) NOT NULL,
  PRIMARY KEY (callId)
);

CREATE TABLE IF NOT EXISTS cdr (
  callId integer(11) unsigned auto_increment,
  name varchar(100) NOT NULL,
  setup_time datetime,
  start_time datetime,
  end_time datetime,
  calling_num varchar(100) NOT NULL default '',
  called_num varchar(100) NOT NULL default '',
  h323confid varchar(35) NOT NULL,
  PRIMARY KEY (callId)
);

/*
 * Since I don't use mysql 5.x there's no trigger t_rm_finished_call definion
 * yet. If you would like to have that trigger in mysql environment see
 * bsdradius.postgresql.sql and rewrite the trigger yourself.
 */
