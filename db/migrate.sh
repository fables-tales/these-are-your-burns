#!/bin/bash

sqlite3 db/app.db "CREATE TABLE echonest_responses (id integer primary key, json text);"
sqlite3 db/app.db "CREATE TABLE upload (id integer primary key, file_name varchar(255));"
sqlite3 db/app.db "CREATE TABLE timings (id integer, sync_method varchar(255), json text, PRIMARY KEY (id, sync_method));"
