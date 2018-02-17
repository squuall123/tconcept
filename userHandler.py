# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import sys, csv, logging, mysql.connector

class user:
    def __init__(self, name, debugger, matricule, qualite):
        self.name = name
        self.debugger = debugger
        self.matricule = matricule
        self.qualite = qualite

class userHandler:
    def __init__(self, configHandler):
        self.configHandler = configHandler
        self.logTableName = "log_" + self.configHandler.numTable

        try:
            #self.conn = mysql.connector.connect(host=configHandler.mysqlServer, user=configHandler.mysqlUser, password=configHandler.mysqlPass, db=configHandler.mysqlDatabase)
            self.conn = mysql.connector.connect(host="localhost", user="tconcept", password="tconcept", db="tconcept")
            self.cursor = self.conn.cursor()
            # On crée la table de journal de l'utilisateur
            query = "CREATE TABLE IF NOT EXISTS %s (date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, event VARCHAR(1000));" % self.logTableName
            self.cursor.execute(query)
            self.conn.commit()
        except mysql.connector.Error as err:
            #TODO: faire remonter ca
            logging.debug(u"Problème mysql: {}".format(err))


    def checkUser(self, matricule):
        # Va regarder si l'utilisateur existe bien dans la liste
        try:
            self.cursor.execute("SELECT * FROM utilisateurs WHERE MATRICULE = %s" , (str(matricule),))
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                row = rows[0]
                if row != None:
                    return user(row[0], row[2] == 1, row[1], row[3] == 1)

        except IOError:
            logging.debug(u"Aucun fichier utilisateur trouvé")
            return ""


    def log(self, message):
        try:
            logging.info(u"Activité stocké: " + message)
            query = "INSERT INTO %s (event) VALUES (\'%s\');" % (self.logTableName, str(message))
            self.cursor.execute(query)
            self.conn.commit()
        except mysql.connector.Error as err:
            #TODO: faire remonter ca
            logging.debug(u"Problème mysql: {}".format(err))
