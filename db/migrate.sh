#!/bin/bash

export PGPASSWORD="lol"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE echonest_responses (id integer primary key, json text);"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE upload (id integer primary key, file_name varchar(255));"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE timings (id integer, sync_method varchar(255), json text, PRIMARY KEY (id, sync_method));"
