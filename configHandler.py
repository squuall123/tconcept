# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import ConfigParser,logging,socket

class configHandler:
    filename = ""
    user = "conf/liste_utilisateur.conf"
    debug= "false"
    logDirectory = "log/"
    refDirectory = "ref/"
    serialPort = "/dev/ttyAMA0"
    serialBaud = 115200
    serialTimeout = 2
    codeAnnulation = "annulation"
    codeSonde = "sonde"
    numTable = "0"
    mysqlServer = "localhost"
    mysqlDatabase = "tconcept"
    mysqlUser = "root"
    mysqlPass = ""


    def __init__(self, filename="conf/defaults.cfg"):
        self.config=ConfigParser.ConfigParser()
        #ip= [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

        try:
            self.config.readfp(open(filename))
        except IOError:
            logging.info('Aucun fichier de config trouvé')
        try:
            self.user = self.config.get('soft', 'user')
            self.debug = self.config.getboolean('soft', 'debug')
            self.logDirectory = self.config.get('soft', 'logDirectory')
            self.refDirectory = self.config.get('soft', 'refDirectory')
            self.codeAnnulation = self.config.get('soft', 'codeAnnulation')
            self.codeSonde = self.config.get('soft', 'codeSonde')
            self.numTable = self.config.get('soft', 'nom')
            self.serialPort = self.config.get('serial', 'port')
            self.serialBaud = self.config.getint('serial', 'baud')
            self.serialTimeout = self.config.getint('serial', 'timeout')
            # Old Fashion
            #self.numTable = "PCE_" + ip.replace('.', '')
            self.mysqlServer = self.config.get('mysql', 'server')
            self.mysqlDatabase = self.config.get('mysql', 'database')
            self.mysqlUser = self.config.get('mysql', 'user')
            self.mysqlPass = self.config.get('mysql', 'pass')
        except ConfigParser.Error:
            logging.debug('Erreur dans le fichier de config')

