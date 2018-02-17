#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector, csv


try:
    conn = mysql.connector.connect(host="localhost",user="root",password="tconcept")
    
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS tconcept");
    cursor.execute("USE tconcept");
    cursor.execute("DROP TABLE IF EXISTS utilisateurs");


    # Création de la table utilisateur
    cursor.execute("CREATE TABLE IF NOT EXISTS utilisateurs (NOM varchar(50) NOT NULL, MATRICULE int(5) NOT NULL, DEBUGGER BOOL NOT NULL, QUALITE BOOL NOT NULL );")

    # Insérer tous les utilisateurs
    with open('liste_utilisateur-02.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            cursor.execute("INSERT INTO utilisateurs (NOM, MATRICULE, DEBUGGER, QUALITE) VALUES (%s, %s, %s, %s)", (row['NOM'], row['MATRICULE'], row['DEBUGGER'], row['QUALITE']))

    conn.commit()
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
      print("Something went wrong: {}".format(err))

