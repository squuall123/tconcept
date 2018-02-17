# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import ConfigParser,logging, csv, time
import RPi.GPIO as GPIO
# Serial library
from serialComHandler import *
#asma
from IOHandler import *
#
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
# TODO: change this
# Pour le bouton
#import RPi.GPIO as GPIO

# Class contenant les options pour une référence
class refConfig:
    refNumber = 0
    # Variables
    ref = ""
    code = ""
    design = ""
    lot = ""


    # Tests
    courant = 0
    continuite = 0
    uartTimeout = 0
    testTimeout = 0
    printTimeout = 0
    # Imprimante
    ZPLFile = ""
    #asma variable
    timebuzzer=0
    etanchiete=0
    isole=0
    pression=0
    tempo1=0
    tempo2=0
    tensionvannemax=0
    pressionoutmax=0
    t=0
 
   
  
   


class refHandler(QObject):
    # definition des signaux
    # en cas d'erreur
    serialError = QtCore.pyqtSignal(str)
    # La liste de test est envoyée
    sendTestDone = QtCore.pyqtSignal()
    #asma point isolé
    sendTestPNCDone = QtCore.pyqtSignal()
    testpointok = QtCore.pyqtSignal()
    #
    # Tout le test est OK
    testOk = QtCore.pyqtSignal()
    default = QtCore.pyqtSignal(str)
    defaultpisol = QtCore.pyqtSignal(str)
    buttonPressed = QtCore.pyqtSignal()
    refConfig = None
    
   
 
    
    def __init__(self, configHandler, serialHandler):
        QObject.__init__(self)
        self.configHandler = configHandler
        self.serialHandler = serialHandler  
        GPIO.setup(21,GPIO.OUT) 
        self.nb=0 
        self.t=0
       
       

    def loadRefFiles(self, refNumber):
        self.refNumber = refNumber
        return self.loadRefCSVFile(refNumber) and self.loadRefConfigFile(refNumber)


    # Chargement du fichier CSV pour une référence
    def loadRefCSVFile(self, refNumber):
        try:
            with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
                self.reader = csv.DictReader(csvfile, delimiter=';')

                return True
        except IOError:
            logging.debug(u'Fichier de CSV de la référence '+ refNumber + u'non trouvé');
            return False


    # Chargement du fichier Config pour une référence
    def loadRefConfigFile(self, refNumber):
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.readfp(open(self.configHandler.refDirectory + refNumber + '.cfg' ))
        except IOError:
            logging.debug(u'Fichier de config de la référence '+ ref + u'non trouvé')
            return False
        try:
            self.refConfig = refConfig()
            # Lire la section variables en premier
            self.refConfig.ref = self.config.get('variables', 'ref')
            self.refConfig.code = self.config.get('variables', 'code')
            self.refConfig.design = self.config.get('variables', 'design')
            self.refConfig.lot = self.config.get('variables', 'lot')

            # Lire la section test
            self.refConfig.courant = self.config.getint('test', 'courant')
            self.refConfig.continuite = self.config.getint('test', 'continuite')
            self.refConfig.uartTimeout= self.config.getint('test', 'uartTimeout')
            self.refConfig.testTimeout= self.config.getint('test', 'testTimeout')
            self.refConfig.printTimeout= self.config.getint('test', 'printTimeout')
            #asma BUZZER
            self.refConfig.timebuzzer= self.config.getfloat('test', 'timebuzzer')
            #ASMA ETANCHIETE
            self.refConfig.etanchiete= self.config.getint('test', 'etanchiete')
            #Asma test point isolé
            self.refConfig.isole= self.config.getint('test', 'isole')
            
            #pression
            self.refConfig.pression= self.config.getfloat('test', 'pression')
          
            #tempo1
            self.refConfig.tempo1= self.config.getfloat('test', 'tempo1')
            
            #tempo2
            self.refConfig.tempo2= self.config.getfloat('test', 'tempo2')
            
            #tension vanne max
            self.refConfig.tensionvannemax= self.config.getfloat('test', 'tensionvannemax')
            
            #pression out max
            self.refConfig.pressionoutmax= self.config.getfloat('test', 'pressionoutmax')
            
            # On indique le fichier ZPL
            self.refConfig.ZPLFile = self.configHandler.refDirectory + refNumber + '.zpl'


            logging.info("[variable]")
            logging.info("ref = " + self.refConfig.ref)
            logging.info("code = " + self.refConfig.code)
            logging.info("design = " + self.refConfig.design)

            logging.info("[test]")
            logging.info("courant = " + str(self.refConfig.courant))
            logging.info("continuite = " + str(self.refConfig.continuite))
            logging.info("uartTimeout = " + str(self.refConfig.uartTimeout))

            logging.info("[print]")
            logging.info("ZPLFile = " + self.refConfig.ZPLFile)

            return True
        except ConfigParser.Error, e:
            logging.debug('Erreur dans le fichier de config de la ref ' + refNumber + ": " + e.message)
            return False


    # prépare la carte pour un nouveau test
    @QtCore.pyqtSlot()
    def sendTest(self):
        print "sendTest"
        try:
            # Envoyer la commande pour vider la liste précédente
            self.serialHandler.sendIT()
            # Envoie la valeur du courant de test
            self.serialHandler.sendCT(self.refConfig.courant)
            # Envoie la valeur du seuil de continuité
            self.serialHandler.sendSC(self.refConfig.continuite)
            with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
                self.reader = csv.DictReader(csvfile, delimiter=';')
                for row in self.reader:
                    if(row['TYPE_TEST'] == "PC"):
                        logging.info('PC 2 ' + row['POINT_TEST_A'] + ' ' +  row['POINT_TEST_B'])
                        self.serialHandler.sendPC_2(int(row['POINT_TEST_A']),  int(row['POINT_TEST_B']))
            self.sendTestDone.emit()
        except SerialError as e:
            logging.debug(e.message)
            self.serialError.emit("Erreur d'envoie:\n" + str(e.message))
            
            
            
    #ASMA TEST POINT ISOLÉ
    
    def sendTestPNC(self):
		print "sendtestpointisolé"
		
		try:
			with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
				self.reader= csv.DictReader(csvfile, delimiter=';') 
				for row  in self.reader:
					if(row['TYPE_TEST'] == "PNC"):
						logging.info('PNC 2 ' + row['POINT_TEST_A'] + ' ' +  row['POINT_TEST_B'])
						self.serialHandler.sendPNC_2(int(row['POINT_TEST_A']),  int(row['POINT_TEST_B']))
						self.sendTestPNCDone.emit()
		except SerialError as e:
			logging.debug(e.message) 
			self.serialError.emit("Erreur d'envoie:\n" + str(e.message))



			


    # Effectue le test
    @QtCore.pyqtSlot(int)
    
    def sg(self, code):
		try:
			if  code != 0x00:
				self.serialHandler.sendTNC(code)
			print "test asma"
			#wait reponse
			rbuf = self.serialHandler.waitTestResponse()
			print rbuf	
			
			if not rbuf:	
				return False
			message =""
			
			if  [0x15,0xF1] == rbuf[0:2]:
				#self.t=2
				self.testRunning = False
				self.testpointok.emit()	
				print "bon"
			elif rbuf[0:2] == [0x17, 0xDF]:
				print "court circuit"
				self.t=1
				point1 = rbuf[2] * 0x100 + rbuf[3]
				point2 = rbuf[4] * 0x100 + rbuf[5]
				# court circuit
				logging.debug("Default de court-circuit")
				with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
					self.reader = csv.DictReader(csvfile, delimiter=';')
					for row in self.reader:
						if int(row['POINT_TEST_A']) == point1:
							message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
							self.serialHandler.lightLED(int(row['POINT_LED_A']))
							self.serialHandler.lightLED(int(row['POINT_LED_B']))
							if int(row['POINT_TEST_A']) == point2:
								message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
								self.serialHandler.lightLED(int(row['POINT_LED_A']))
								self.serialHandler.lightLED(int(row['POINT_LED_B']))
							if int(row['POINT_TEST_B']) == point1:
								message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
								self.serialHandler.lightLED(int(row['POINT_LED_A']))
								self.serialHandler.lightLED(int(row['POINT_LED_B']))
							if int(row['POINT_TEST_B']) == point2:
								message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
								self.serialHandler.lightLED(int(row['POINT_LED_A']))
								self.serialHandler.lightLED(int(row['POINT_LED_B']))
						
							self.defaultpisol.emit(message)
							self.testRunning = False
						   
							logging.debug(message) 
			elif rbuf[0:2] == 0xD0:
				print "coupure"
				self.t=1	
									
		except  SerialError as e:
			return False					
		
			


		
    def startTest(self, code):
        try:
            if code != 0x00:
                # Effectue le test chargé juste avant
          
                self.serialHandler.sendTC(code)
            # Attend une réponse
        
            rbuf = self.serialHandler.waitTestResponse()
            if not rbuf:
                # Do nothing
                return False
            message = ""
 
            if rbuf[0] == 0x00:
                self.testRunning = False
                #self.serialHandler.buzzeron()
                GPIO.output(21, 1)
                time.sleep(self.refConfig.timebuzzer)
                GPIO.output(21, 0)
                self.serialHandler.turnOffLED()
                #self.serialHandler.buzzerof()
                self.testOk.emit()
             
                

                
            elif rbuf[0] == 0xDF:
                #asma modif
                
                if self.nb==1:
					#self.serialHandler.buzzeron()
					GPIO.output(21, 1)
					time.sleep(self.refConfig.timebuzzer)
					GPIO.output(21, 0)
					self.serialHandler.turnOffLED()
					#self.serialHandler.buzzerof()
        
                #
                point1 = rbuf[1] * 0x100 + rbuf[2]
                point2 = rbuf[3] * 0x100 + rbuf[4]
                # court circuit
                logging.debug("Default de court-circuit")
                with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
                    self.reader = csv.DictReader(csvfile, delimiter=';')
                    for row in self.reader:
                        if int(row['POINT_TEST_A']) == point1:
							#asma elimine \n
                            message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
                            #message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "   "
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_A']) == point2:
                            message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_B']) == point1:
                            message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_B']) == point2:
                            message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                    self.testRunning = False
                    self.default.emit(message)
                    logging.debug(message)
            elif rbuf[0] == 0xD0:
                #asma modif
                #self.serialHandler.turnOffLED()
                if self.nb==1:
					#self.serialHandler.buzzeron()
					GPIO.output(21, 1)
					time.sleep(self.refConfig.timebuzzer)
					GPIO.output(21, 0)
					self.serialHandler.turnOffLED()
					
					#self.serialHandler.buzzerof()
 
				
                #
                point1 = rbuf[1] * 0x100 + rbuf[2]
                point2 = rbuf[3] * 0x100 + rbuf[4]
                # coupure
                message = "Coupure de connecteur:\n"
                with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
                    self.reader = csv.DictReader(csvfile, delimiter=';')
                    for row in self.reader:
                        if int(row['POINT_TEST_A']) == point1:
							#asma eliminer \n
                            message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
                            #message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] +"      "
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_A']) == point2:
                            message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_B']) == point1:
                            message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                        if int(row['POINT_TEST_B']) == point2:
                            message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
                            self.serialHandler.lightLED(int(row['POINT_LED_A']))
                            self.serialHandler.lightLED(int(row['POINT_LED_B']))
                    self.testRunning = False
                    self.default.emit(message)
                   
                    logging.debug(message)
                    self.nb=1
            elif rbuf[0] == 0xDC:
                logging.debug("Erreur carte: pas de liste dans la carte")
                self.serialError.emit("Erreur carte: pas de liste dans la carte") 
            #elif rbuf[0] == 0xD7:
				#print "défaut hors tolérance"
				#self.serialHandler.turnOffLED()
				#if self.nb==1:
					#self.serialHandler.buzzeron()
					#time.sleep(self.refConfig.timebuzzer)
					#self.serialHandler.buzzerof()
					
				#point1 = rbuf[1] * 0x100 + rbuf[2]  
				#point2 = rbuf[3] * 0x100 + rbuf[4]   
				#print point1
				#print point2
				#message="défaut hors tolérance:\n"
				#with  open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
					#self.reader = csv.DictReader(csvfile, delimiter=';')
					#for row in self.reader:
						#if int(row['POINT_TEST_A']) == point1:
							#message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						#if  int(row['POINT_TEST_A']) == point2:
							#message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						#if int(row['POINT_TEST_B']) == point1:
						#	message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
						#if  int(row['POINT_TEST_B']) == point2:
							#message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
					#self.testRunning = False   
					#self.default.emit(message)  
					#logging.debug(message)
					#self.nb=1      
            elif rbuf[0:2]==[0x15,0xF1]:
				print "yess"
				self.testRunning = False
				self.testpointok.emit()	
            elif rbuf[0:2]==[0x17, 0xDF]:
				print "court circuit"
				point1 = rbuf[2] * 0x100 + rbuf[3]
				point2 = rbuf[4] * 0x100 + rbuf[5]
                # court circuit
				logging.debug("Default de court-circuit")
				with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
					self.reader = csv.DictReader(csvfile, delimiter=';')
					for row in self.reader:
						if int(row['POINT_TEST_A']) == point1:
							#asma elimine \n
							message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_A']) == point2:
							message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_B']) == point1:
							message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_B']) == point2:
							message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
					self.testRunning = False
					self.defaultpisol.emit(message)
					logging.debug(message)
            elif rbuf[0:2]==[0x17, 0xD0]:
				print "coupure point isolé"
				point1 = rbuf[2] * 0x100 + rbuf[3]
				point2 = rbuf[4] * 0x100 + rbuf[5]
                # court circuit
				logging.debug("coupure point isolé")
				with open(self.configHandler.refDirectory + self.refNumber + '.csv') as csvfile:
					self.reader = csv.DictReader(csvfile, delimiter=';')
					for row in self.reader:
						if int(row['POINT_TEST_A']) == point1:
							#asma elimine \n
							message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_A']) == point2:
							message += row['CONNECTEUR_A'] + ' voie '+ row['VOIES_A'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_B']) == point1:
							message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
						if int(row['POINT_TEST_B']) == point2:
							message += row['CONNECTEUR_B'] + ' voie '+ row['VOIES_B'] + " - " + row['COMMENTAIRE'] + "\n"
					self.testRunning = False
					self.defaultpisol.emit(message)
					logging.debug(message)				
            elif rbuf[0:2] == 0xDC:
                logging.debug("Erreur carte: pas de liste dans la carte")
                self.serialError.emit("Erreur carte: pas de liste dans la carte") 				

			

        except SerialError as e:
            #logging.debug(e.message)
            #self.serialError.emit("Erreur lors du test:\n" + str(e.message))
            # Do nothing
            return False
    def  startTestPNC (self, code):
		try:
			if code != 0x00:
				self.serialHandler.sendTNC(code)
			self.startTest(0x00)
               
		except SerialError as e:
            #logging.debug(e.message)
            #self.serialError.emit("Erreur lors du test:\n" + str(e.message))
            # Do nothing
			return False
		
            
            
 
