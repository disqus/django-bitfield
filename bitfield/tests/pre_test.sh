#!/bin/sh
if [[ $DB = "postgres" ]]; then
    psql -c 'create database bitfield;' -U postgres;
fi
