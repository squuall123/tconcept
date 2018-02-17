# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import logging, datetime, time, cups

class PrintError(Exception):
    pass

class printHandler:
    bufToPrint = ""
    tmpPrintFile = 'tmp/printTmpFile'
    def __init__(self, configHandler):
        self.conf = configHandler

    def testConnexion(self):
        conn = cups.Connection()
        printers = conn.getPrinters()
        connexion = False
        for printer in printers:
            print printer, printers[printer]['device-uri']
            if printer == "TSC_TTP-247":
                connexion = True
        return connexion


    def printTicket(self, refHandler):
        self.ref = refHandler.refConfig
        str_time =  time.strftime("%H"+":"+"%M"+":"+"%S")
        str_date = datetime.date.today().strftime("%d/%m/%Y")

        try:
            f1 = open(self.ref.ZPLFile, 'r')
            f2 = open(self.tmpPrintFile, 'w')
        except IOError as e:
            raise PrintError("impossible d'ouvrir le fichier ZPL")
        for line in f1:
            #TODO: change this
            f2.write( line.replace('-REF-', self.ref.ref).replace('-TIME-', str_time).replace('-DATE-', str_date).replace('-DESIGNATION-', self.ref.design).replace('-CODE-', self.ref.code ).replace('-LOT-', self.ref.lot))
            self.bufToPrint += line.replace('-REF-', self.ref.ref).replace('-TIME-', str_time).replace('-DATE-', str_date).replace('-DESIGNATION-', self.ref.design).replace('-CODE-', self.ref.code ).replace('-LOT-', self.ref.lot) + "\n"
        
        f1.close()
        f2.close()
        print self.bufToPrint

        conn = cups.Connection()
        printers = conn.getPrinters()
        conn.printFile("TSC_TTP-247", self.tmpPrintFile, 'TSC_TTP-247 demo', {}) 


        logging.info(u"Ticket pour la référence:" + self.ref.ref + " et design: " + self.ref.design + u" imprimé le " + str_date + u" à " + str_time)



