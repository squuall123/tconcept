#!/bin/bash
mysql -u root -ptconcept << EOF
# Drop and create database (from scratch)
CREATE DATABASE tconcept;
DROP DATABASE IF EXISTS tconcept; 
CREATE DATABASE playence_media; 
USE tconcept;



EOF
