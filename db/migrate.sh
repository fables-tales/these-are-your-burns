#!/bin/bash

export PGPASSWORD="lol"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE IF NOT EXISTS echonest_responses (id integer primary key, json text);"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE IF NOT EXISTS upload (id integer primary key, file_name varchar(255));"
psql --host=127.0.0.1 burns burns -c "CREATE TABLE IF NOT EXISTS timings (id integer, sync_method varchar(255), json text, PRIMARY KEY (id, sync_method));"
