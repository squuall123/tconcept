# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import sys, logging, time
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QObject
from threading import Timer


# nos fenêtres
from UI import *

# Des fonctions de traitement
from configHandler import *
from userHandler import *
from refHandler import *
from printHandler import *
from serialComHandler import *
from IOHandler import *

# Gere le workflow de l'appli
# les fenêtres emettent des signaux, le eventHandler agis en conséquence
class eventHandler (QObject):
    # Definition des signaux
    # on utilise cette methode pour le port serie sinon il bloque l'UI
    sendTest = QtCore.pyqtSignal()
    #asma point isolé
    sendTestPNC=QtCore.pyqtSignal()
    #
    startTest = QtCore.pyqtSignal(int)
    #asma point isolé
    startTestPNC = QtCore.pyqtSignal(int)
    #
    updateUI = QtCore.pyqtSignal()
    returnToUser = QtCore.pyqtSignal()
    setScanWindow = QtCore.pyqtSignal(str, str, QtGui.QColor)
    returnToRef = QtCore.pyqtSignal(str)
    ticket = False
    startTestTime = 0
    bestTestTime = 0
    x1=0
    x2=0
    p=0
    v1=0
    p1=0
    tesionout=0
    mode = "start"
    etanche=0
    isole=0

    # Compteur pour les pièces
    countGoodPieces = 0
    countWrongPieces = 0

    def __init__(self, configHandler):
        # init
        QObject.__init__(self)

        self.configHandler = configHandler;
        self.serialHandler = serialComHandler(self.configHandler)
        self.refHandler= refHandler
        # Pour la gestion entrée/sortie
        self.IOHandler = IOHandler(self.serialHandler, self.IOCallback)
        # lance l'appli  de base
        self.ui = UI(self.configHandler, self.IOHandler)
        self.updateUI.connect(self.ui.updateUI)
        self.returnToUser.connect(self.ui.returnToUser)
        self.returnToRef.connect(self.ui.returnToRef)
        self.setScanWindow.connect(self.ui.setScanWindow)
        self.IOHandler.verrin("orange")
      
     

        # Faire les tests de démarrage

        # Pour le test reseaux, on test si un fichier reseau est accessiblei
        test =0
        try:
            # Connexion a la database + recupération user
            self.userHandler = userHandler(self.configHandler)
            # TODO: Change this
            with open('conf/test.conf'):
                logging.info(u'Connexion réseau active')
                test+=1
        except IOError:
            logging.debug(u'Erreur! Aucune connexion réseau au démarrage')
            self.ui.setInfoWindow("Erreur:\nAucune connexion réseau" , QtCore.Qt.red)

       
	
        
        # Test Carte
        if test == 1:
            try:
                # Vider la liste pour tester si la carte réponds
                self.serialHandler.sendIT()
                logging.info('Connexion avec la carte active')
                # Eteindre les leds au démarrage
                self.serialHandler.turnOffLED()
                test+=1
                #asma
                
                #self.serialHandler.sendANA(0x03,0xE8)
                #self.x1=self.IOHandler.testEA(1)
              
            except SerialError as e:
                logging.debug("Erreur de test port série:" + str(e.message))
                self.ui.setInfoWindow("Erreur:\nAucune connexion avec la carte" , QtCore.Qt.red)
                
                      
        # Test imprimante
        if test == 2:
            # TODO: a vérifier
            self.printHandler = printHandler(self.configHandler)
            if self.printHandler.testConnexion():
                test+=1
            else:
                logging.debug(u"Erreur: Aucune connexion avec l\'imprimante")
                self.ui.setInfoWindow(u"Erreur:\nAucune connexion avec l\'imprimante" , QtCore.Qt.red)


        # Test air comprimé
        if test == 3:
            # On désactive le verin:
            self.IOHandler.deActivateActuator()
          
            
           
           
		
       
            
		
            if self.IOHandler.testAirPressure():
                test+=1
            else:
                logging.debug(u"Erreur: Pas d'air comprimé")
                self.ui.setInfoWindow(u"Erreur:\nPas d'air comprimé" , QtCore.Qt.red)
                 

        self.ui.startTest = test
    

        if test == 4:
            self.ui.scanDone.connect(self.scan)
            self.mode = "user"
            self.previousMode = "user" 
            self.ui.userWindow()
            
        


         
           
        
        # TODO: For test purpose only, remove this for production
        #self.mode = "ref"
        #self.ui.scanDone.emit('1')
    


###########
###
###  Gestion des scan (douchette)
###
###########

    # Des qu'on recoit un scan, on le traite ici
    @QtCore.pyqtSlot(str)
    def scan(self, text):
        # Check le user
        if self.mode == "user":
            self.user = self.userHandler.checkUser(text)
            if self.user != None:
                if self.user.name != "":
                    if self.user.qualite != True:
                        self.ui.user = "Utilisateur: "+ self.user.name
                        self.updateUI.emit()
                    # On arrive ici si le matricule rentré par l'utilisateur est juste et autorisé !
                    logging.info(u'Utilisateur ' + self.user.name + ', matricule ' + text  +u' autorisé')
	       	    self.userHandler.log('Utilisateur ' + self.user.name + ', matricule ' + text  +u' autorise')
                    self.mode = "ref"
                    self.ui.refWindow(name = self.user.name)
                    if self.user.debugger == True:
                        self.ui.showLog()
                    else:
                        self.ui.hideLog()

                else:
                    logging.info(u'Utilisateur ' + self.user.name + ', matricule ' + text  +u' non trouvé ou non autorisé')
                    self.ui.userWindow(error=u'Utilisateur non trouvé: recommencez')
            else:
                logging.info(u'Utilisateur, matricule ' + text  +u' non trouvé ou non autorisé')
                self.ui.userWindow(error=u'Utilisateur non trouvé: recommencez')

        elif self.mode == "lock":
            #TODO
            # on est en mode lock, le reponsable qualité doit pouvoir débloquer le système
            self.user = self.userHandler.checkUser(text)
            if self.user != None:
                if self.user.qualite == True:
                    # L'utilisateur fait partie de la qualité, on lui présente le panneau dévérouillage
                    logging.info(u'Utilisateur ' + self.user.name + ', matricule ' + text  +u' autorisé pour la qualité')
                    self.ui.setInfoWindow(u"Appuyer sur le bouton start\nPour déverouiller le vérin", QtCore.Qt.green)
                    self.serialHandler.turnOffLED()
                    self.mode = "qualite"
                else:
                    self.setScanWindow.emit(u"Utilisateur non autorisé", u"Appeler un responsable qualité", QtCore.Qt.red)
                    logging.debug("Utilisateur non autorisee pour la qualite")
            else:
                self.setScanWindow.emit(u"Utilisateur non autorisé", u"Appeler un responsable qualité", QtCore.Qt.red)
                logging.debug("Utilisateur non autorisee pour la qualite")
        elif self.configHandler.codeSonde == text and self.user.debugger == True:
            # On passe en mode sonde !
            self.mode = "sonde"
            self.IOHandler.verrin("orange")
            # Active le mode sonde sur la carte
            self.serialHandler.sendPS(1)
            self.ui.setInfoWindow(u"Appuyé sur CANCEL pour arreter le test", QtCore.Qt.green)
            self.ui.testFaisceau.connect(self.testFaisceau)
            # TODO: you should change this ...
            self.ui.startTimeAndCount(1)
            self.ui.timeFrame.hide()
            self.ui.countFrame.hide()

        # Check la reference
        elif self.mode == "ref":
            self.ref = text
            if self.configHandler.codeAnnulation == text:
                self.ui.resetTimer()
                self.ui.stopTimer()
                self.mode = "user"
                self.previousMode = "user"
                self.ui.userWindow()
            else: # charge les fichier correspondants
			
                self.refHandler = refHandler(self.configHandler, self.serialHandler)
                if self.configHandler.codeAnnulation != text and self.refHandler.loadRefFiles(text):
                    self.userHandler.log('Fichiers correctement charge pour la reference: ' + text)
                    logging.info('Fichiers correctement chargé pour la référence: ' + text)
                    self.ui.setInfoWindow(u"Fichiers chargé:\n" + self.refHandler.refConfig.design + "\nChargement en cours", QtCore.Qt.green)
                    # on connecte les signaux
                    # ils permettent de dérouler le programme comme il faut
                    self.sendTest.connect(self.refHandler.sendTest)
                    #asma point isolé
                    self.sendTestPNC.connect(self.refHandler.sendTestPNC)
                   
                   
                     #
                    self.ui.buttonPressed.connect(self.IOCallback)
                    self.ui.testFaisceau.connect(self.testFaisceau)
		    self.refHandler.serialError.connect(self.serialError)
                    self.startTest.connect(self.refHandler.startTest)
                    self.startTestPNC.connect(self.refHandler.startTestPNC)
                    self.refHandler.sendTestDone.connect(self.sendTestDone)
                    #asma point isolé
                    self.refHandler.sendTestPNCDone.connect(self.sendTestPNCDone)
                    #
                    self.refHandler.testOk.connect(self.testOk)
                    self.refHandler.default.connect(self.default)
                    self.refHandler.defaultpisol.connect(self.d)
                    self.refHandler.testpointok.connect(self.testpointok)
                    
                    
                    #asma
              
                    # Et on lance la thread
                    # pour eviter que le port serie ne bloque l'appli
                    #self.refHandler_thread = QtCore.QThread()
                    #self.refHandler.moveToThread(self.refHandler_thread)
                    #self.refHandler_thread.start()
                    # Envoie du CSV à la carte
                    #asma envoie de la tension vers la  vanne 
                   
                    self.mode = "sendTest"
                   
                    self.sendTest.emit()
                else:
                    logging.info(u'Une erreur est survenue lors du chargement des fichiers de la référence: ' + self.ref)
                    self.ui.refWindow(name = self.user.name, error=u"Erreur de chargement: \nfichiers non trouvé pour la référence " + self.ref)
        elif self.mode == "scanPrint":
            if self.ticket == False:
                #Pas de ticket, affichage et on recommence
                self.setScanWindow.emit(u"Pas de présence ticket", "Scannez le ticket", QtCore.Qt.green)
            elif text == self.refHandler.refConfig.code or text == self.configHandler.codeAnnulation:
                self.userHandler.log("etiquette imprime et scanne")
                # On regarde si on a le meilleur temps
                now = QtCore.QDateTime.currentDateTime()
                print "-Meileur temps-"
                print  -now.secsTo(self.startTestTime)
                print self.bestTestTime
                if self.bestTestTime < -now.secsTo(self.startTestTime):
                    self.ui.updateBestTime( -now.secsTo(self.startTestTime))
                    self.userHandler.log("nouveanbu record %s" %  -now.secsTo(self.startTestTime))
                # Test ok dans son ensemble on augmente le nombre de pièce
                self.ticket = True
                self.increaseGoodPieces()
                # Deverrouillage pièce
                # TODO: change this
                try:
                    self.IOHandler.deActivateActuator()
                    #asma
                    self.refHandler.nb=0 
                    self.updateUI.emit()
                    self.userHandler.log("verin desactive pour cause annulation")
                except SerialError as e:
                    logging.debug("Probleme lors de la desactivation du verin: " + e.message)
                logging.info(u"On annule le probleme")
                # On test des nouvelles pièces
                self.ui.setInfoWindow("Retirez le faisceau", QtCore.Qt.green)
                self.mode = "attentepasfaisceau"
            elif text != self.refHandler.refConfig.code:
                logging.debug("Ticket presente incorrecte")
                self.setScanWindow.emit("Reference incorrecte\nRecommencez", "Scannez le ticket", QtGui.QColor(0xFF, 0xA8, 0x00))


        elif self.mode == "default":
            if text == configHandler.codeAnnulation:
                logging.info(u"On annule le problème")
                self.sendTestDone()
                self.increaseWrongPieces()
                self.serialHandler.turnOffLED()
				
    # Si on arrive ici c'est que tout va bien
    # on passe à la suite
    @QtCore.pyqtSlot()
    def sendTestDone(self):
        self.mode = "attenteFaisceau"
        self.ui.showProgName(self.refHandler.refConfig.design)
        self.ui.setInfoWindow(u"Test prêt: attente faisceau", QtGui.QColor(0xFF, 0x9C, 0x00))
        self.IOHandler.verrin("green")
       
        #asma evoie la tension et  lire l etat d etanchieté
      
      
       
        self.etanche=self.refHandler.refConfig.etanchiete
        self.isole=self.refHandler.refConfig.isole
        self.ui.etanche1=self.etanche
        self.updateUI.emit()
       # if self.etanche==1:
			#self.tension()
		
        self.ui.startTimeAndCount(self.refHandler.refConfig.testTimeout)
        
    #ASMA TEST PONIT ISOLÉ
    
    def sendTestPNCDone(self):
		self.ui.showProgName(self.refHandler.refConfig.design)
		self.ui.setInfoWindow(u"Test point isolé prêt", QtGui.QColor(0xFF, 0x9C, 0x00))
		self.IOHandler.verrin("green")
		self.startTestPNC.emit(0x51)


###########
###
### Fonction de timer 
###
###########

    # Fonction qui va être appelé par l'UI tant qu'on a pas de faisceau
    @QtCore.pyqtSlot(int)
    def testFaisceau(self, timeElapsed):
        if self.mode == "attenteFaisceau":
		
            if self.IOHandler.faisceau == 1:
                self.startTestTime = QtCore.QDateTime.currentDateTime()
                self.userHandler.log('Presence faisceau active')
                #TODO: change this
                # Activer le verrin en premier
                try:
                    self.IOHandler.activateActuator()
                    self.updateUI.emit()
                    logging.info(u"Vérin activé")
                except SerialError as e:
                    logging.debug("Problème de verrouillage vérin: " + e.message)
                self.ui.setInfoWindow(u"Faisceau Présent\nAppuyer sur le bouton Start\npour lancer le test", QtCore.Qt.green)
                logging.debug(u"Faisceau Présent: attente lancement test")
                self.ui.resetTimer()
                self.mode = "test"
            elif timeElapsed >= self.refHandler.refConfig.testTimeout and timeElapsed <= self.refHandler.refConfig.testTimeout + 1 :
                
                self.ui.setInfoWindow(u"Chargement du faisceau trop lent\nNotification dans le journal", QtCore.Qt.red)
                logging.debug(u"Chargement du faisceau trop lent: Notification dans le journal")
        elif self.mode == "test" or self.mode == "runningtest" or self.mode == "default":
            # on attends de nouveau une nouvelle réponse
            if timeElapsed >= self.refHandler.refConfig.testTimeout:
                # Verrouillage
                self.mode = "lock"
                self.ui.stopTimer()
                self.IOHandler.verrin("red")
                # on envoie une annulation de test
                self.serialHandler.cancelTest()
                self.ui.setInfoWindow(u"Temps écoulé\nDéverrouillage faisceau\nEnlever le faisceau", QtCore.Qt.red)
                logging.debug(u"Temps écoulé pour le test. DéVerrouillage faisceau")
                self.IOHandler.deActivateActuator()
                #asma
                self.refHandler.nb=0 
                self.updateUI.emit()
                self.userHandler.log("verin desactive pour cause temps test ecoule")
                self.mode = "attentepasfaisceau"
                self.increaseWrongPieces()
            else:
                self.startTest.emit(0x00)
                self.startTestPNC.emit(0x00)
        elif self.mode == "scanPrint":
            if timeElapsed >= self.refHandler.refConfig.printTimeout:
                # Verrouillage
                self.mode = "lock"
                self.ui.stopTimer()
                self.IOHandler.verrin("red")
                self.setScanWindow.emit(u"Temps dépose etiquette écoulé\nVerrouillage faisceau", u"Appeler un responsable qualité", QtCore.Qt.red)
                logging.debug(u"Procédure trop lente: Verrouillage faisceau")
        elif self.mode == "sonde":
            pin = self.IOHandler.checkSonde()
            if pin != None:
                self.ui.setInfoWindow("Mode sonde actif\nPin active " + str(pin) , QtGui.QColor(0xFF, 0xA8, 0X00))
#asma etanchiété
    @QtCore.pyqtSlot()
    def testOk(self):	 
	   
		 if self.mode== "runningtest" or self.mode == "default":
			 print "Test electrique ok"
			
			 self.ui.setInfoWindow("Test electrique Ok\n", QtCore.Qt.green)
			 
			 if self.isole==1:
				 self.sendTestPNC.emit()
			 elif self.etanche==1:
				 logging.info(u"Test etanchiété en cours")
				 self.ui.setInfoWindow(u"Test electrique ok\nTest etanchietie en cours", QtCore.Qt.green)
				 self.ETANCHIETE()
			 else :
				 self.mode = "scanPrint"
				 try:
					 self.printHandler.printTicket(self.refHandler)
				 except PrintError as e:
					 self.mode = "error"
					 logging.debug(u"Problème d'impression: " + e.message)
					 self.ui.setInfoWindow(u"Problème d'impression:\n" + e.message, QtCore.Qt.red)
				 self.ui.setInfoWindow("Test  Ok\nAttente etiquette", QtCore.Qt.green)
				 self.ui.startTimeAndCount(self.refHandler.refConfig.printTimeout) 
			 
			 
			 
			 #ASMA TEST POINT ISOLÉ
	
            
    def testpointok(self):
		self.ui.setInfoWindow("Test points isolés  Ok\n", QtCore.Qt.green)
		print "Test point isolé  Ok"
		if self.etanche==1:
			logging.info(u"Test etanchiété en cours")
			self.ui.setInfoWindow(u"Test ok\nTest etanchietie en cours", QtCore.Qt.green)
			self.ETANCHIETE()
		else:
			self.mode = "scanPrint"
			try :
				self.printHandler.printTicket(self.refHandler)
			except PrintError as e:
				self.mode = "error"
				logging.debug(u"Problème d'impression: " + e.message)
				self.ui.setInfoWindow(u"Problème d'impression:\n" + e.message, QtCore.Qt.red)
			self.ui.setInfoWindow("Test  Ok\nAttente etiquette", QtCore.Qt.green)
			self.ui.startTimeAndCount(self.refHandler.refConfig.printTimeout) 

			 
		 
		
           

    def increaseGoodPieces(self):
        self.countGoodPieces += 1
        self.ui.displayGoodCounter(self.countGoodPieces)
        
    def d(self,message):
		print "erreur"
		self.ui.setInfoWindow("Default test point isole: " + message + "Verifier l'erreur", QtCore.Qt.red)
		logging.debug("Default: \n" + message)
		self.serialHandler.cancelTest()
		
		print "lock"
		self.setScanWindow.emit(u"Boitier déverroillé\n", u"Appeler un responsable qualité", QtCore.Qt.red)
		logging.debug(u"Boitier déverroillé\nEnlever le faisceau")
		self.mode = "lock"
		self.refHandler.nb=0 
		self.increaseWrongPieces()
		
		

             
      
    

    def increaseWrongPieces(self):
        self.countWrongPieces += 1
        self.ui.displayWrongCounter(self.countWrongPieces)
 
    #asma
    def tension (self):
		self.p=self.refHandler.refConfig.pression
		self.v1=self.refHandler.refConfig.tensionvannemax
		self.p1=self.refHandler.refConfig.pressionoutmax
		self.tensionout=((self.p * self.v1)/self.p1)*100
		print self.tensionout
		self.VH = int(self.tensionout) >> 8
		self.VL = int(self.tensionout) - self.VH * 0x100
		print self.VH
		print self.VL
		self.serialHandler.sendANA(self.VH,self.VL)

    @QtCore.pyqtSlot(str)
    def default(self, message):
        logging.debug("Default: \n" + message)
        self.mode = "default"
        #asma
        self.ui.setInfoWindow("Default: " + message + "Verifier l'erreur", QtCore.Qt.red)
        #self.ui.setInfoWindow("Default: " + message + "\nVerifier l'erreur", QtCore.Qt.red)
    #def ev2(self):
		#if self.t1==1:
		#	self.t2=0
			#self.serialHandler.Desactivelectrovane2()
			#self.t2=1
		#return self.t2
   # def ev1(self,t1):
		#self.t1=0
		#self.serialHandler.Desactivelectrovane1()
		#self.t1=1
		#return self.t1


	
 

    def ETANCHIETE(self):
		
		#try:
			#self.serialHandler.Activelectrovane1()
			#self.serialHandler.Active2()
			#self.serialHandler.Activelectrovane1()
			#self.serialHandler.Active2()    
			#time.sleep(self.refHandler.refConfig.tempo1)
			#self.serialHandler.Desactivelectrovane1()
			#time.sleep(self.refHandler.refConfig.tempo2)
			#self.serialHandler.Desactivelectrovane2()
			#self.ui.setInfoWindow("Test etanchiete en cours \nAttente etiquette", QtCore.Qt.green)  
		#except  SerialError as e:
			#logging.debug("Probleme lors de l activation du electrovanne: " + e.message)  
		self.serialHandler.Activelectrovane1()
		self.serialHandler.Active2() 
		    
		time.sleep(self.refHandler.refConfig.tempo1)
		self.serialHandler.Desactivelectrovane1()
		time.sleep(self.refHandler.refConfig.tempo2)
		self.updateUI.emit()
		self.serialHandler.Desactivelectrovane2()
		time.sleep(3)
	
		#Timer(2,self.ev1,()).start()
		#Timer(2.5,self.ev2,()).start()
		self.x1=self.IOHandler.testEA(1)
		print "x1"
		print self.x1
		
		self.x2=self.IOHandler.testEA(2)
		print "x2"
		print self.x2
		if 	self.x1>290 and self.x1<350 and self.x2<87:
		#if 	self.x2==1 and self.x1==0:
			logging.info("Test etanchiété ok")
			self.mode = "scanPrint"
			try:
				self.printHandler.printTicket(self.refHandler)
			except PrintError as e:
				self.mode = "error"
				logging.debug(u"Problème d'impression: " + e.message)
				self.ui.setInfoWindow(u"Problème d'impression:\n" + e.message, QtCore.Qt.red)
			self.ui.setInfoWindow("Test etanchiete Ok\nAttente etiquette", QtCore.Qt.green)
			self.ui.startTimeAndCount(self.refHandler.refConfig.printTimeout) 
		else :
			logging.info(u"Test etanchiété non ok")
			self.ui.setInfoWindow(u"Test etanchiété non ok", QtCore.Qt.red)
		
		

	
				
				
		
###
###  Fonction de gestion evenement
###
###########


    @QtCore.pyqtSlot(str)
    def IOCallback(self, event):
        if event == "INPUTS":
            print self.IOHandler.faisceau 
            print self.mode
            if self.IOHandler.aircomprime == 0:
                self.previousMode = self.mode
                self.mode = "block"
                logging.debug(u"Erreur: Pas d'air comprimé")
                self.ui.setInfoWindow(u"Erreur:\nPas d'air comprimé" , QtCore.Qt.red)
            elif self.IOHandler.etiquette == 1 and self.mode == "scanPrint":
                logging.info(u"Etiquette présente après impression")
                self.setScanWindow.emit(u"Etiquette présente après impression", u"Scannez l'étiquette", QtCore.Qt.green)
                self.ticket = True
            elif self.IOHandler.faisceau == 0 and self.mode == "attentepasfaisceau":
                self.sendTestDone()
            elif self.mode == "block":
                self.mode = self.previousMode
            elif self.mode == "cancelError" and self.IOHandler.faisceau == 0:
                self.sendTestDone()
                self.increaseWrongPieces()
            elif self.IOHandler.faisceau == 0 and self.mode == "test":
                self.mode = "attenteFaisceau"
                self.ui.setInfoWindow(u"Test prêt: attente faisceau", QtGui.QColor(0xFF, 0x9C, 0x00))
                self.ui.startTimeAndCount(self.refHandler.refConfig.testTimeout)
                self.IOHandler.verrin("green")

        elif event == "START":
            logging.info("appui sur start")
            self.userHandler.log("Appui sur start")
            if self.mode == "test":
                # On attends un appui sur le bouton pour commencer le test
                self.ui.setInfoWindow("Test en cours", QtCore.Qt.blue)
                self.ui.startTimeAndCount(1)
                self.startTest.emit(0x51)
                self.mode = "runningtest"
            if self.mode == "qualite":
                self.IOHandler.deActivateActuator()
                #ASMA
                self.refHandler.nb=0 
                #
                self.updateUI.emit()
                self.userHandler.log("verin desactive pour cause qualite")
                self.increaseWrongPieces()
                self.mode = "attentepasfaisceau"
                self.ui.setInfoWindow("Retirez le faisceau", QtCore.Qt.green)
        elif event == "CANCEL":
            logging.info("appui sur cancel")
            self.userHandler.log("Appui sur cancel")
            if self.mode == "error":
                # En cas d'erreur, si on appuie sur le bouton, on revient sur le scan de ref
                logging.info(u"On annule le problème")
                self.serialHandler.turnOffLED()
                self.mode == "cancelError"
            if self.mode == "sonde" or self.mode == 'ref':
                self.serialHandler.turnOffLED()
                logging.info("On reviens au login")
                self.serialHandler.sendPS(0)
                self.ui.user = ""
                self.returnToUser.emit()
                self.updateUI.emit()
                self.mode = "user"
                self.previousMode = "user"
            elif self.mode == "attenteFaisceau" or self.mode == "runningtest" or self.mode == "sendTest":
                self.returnToRef.emit(self.user.name)
                self.mode = "ref"
            if self.mode == "test":
                self.serialHandler.turnOffLED()
                self.ui.showProgName(self.refHandler.refConfig.design)
                self.ui.setInfoWindow(u"Test prêt: attente faisceau", QtGui.QColor(0xFF, 0x9C, 0x00))
                self.IOHandler.verrin("green")
                self.ui.startTimeAndCount(self.refHandler.refConfig.testTimeout)
                self.IOHandler.deActivateActuator()
                #ASMA
                self.refHandler.nb=0 
                self.updateUI.emit()
                self.userHandler.log("verin desactive pour cause CANCEL")
            if self.mode == "default":
                self.serialHandler.turnOffLED()
                self.serialHandler.cancelTest()
                self.ui.setInfoWindow(u"Faisceau Déverouillé\nRetirez le faisceau", QtGui.QColor(0xFF, 0x9C, 0x00))
                self.IOHandler.deActivateActuator()
                #asma
                self.refHandler.nb=0 
                self.updateUI.emit()
                self.userHandler.log("verin desactive pour cause abandon test cause defaut")
                self.mode = "attentepasfaisceau"
                self.increaseWrongPieces()
            if self.mode == "scanPrint":
                # Verrouillage
                self.mode = "lock"
                self.ui.stopTimer()
                self.IOHandler.verrin("red")
                self.setScanWindow.emit(u"Cancel etiquette\nVerrouillage faisceau", u"Appeler un responsable qualité", QtCore.Qt.red)
                logging.debug(u"Procédure trop lente: Verrouillage faisceau")

        # On redessine la GUI
        self.updateUI.emit()

    # On a appuyer sur le bouton
    # DEPRECATED
    @QtCore.pyqtSlot(str)
    def buttonPressed(self, buttonPin):
        if buttonPin == 'q':
            if self.mode == "user":
                self.ui.userWindow()
                logging.info('Relance de l\'appli')
        else:
            logging.debug("Bouton appuyé")
            
            if self.mode == "test":
                # On attends un appui sur le bouton pour commencer le test
                self.ui.setInfoWindow("Test en cours", QtCore.Qt.blue)
                self.startTest.emit(0x51)
                self.mode = "runningtest"
            elif self.mode == "error":
                # En cas d'erreur, si on appuie sur le bouton, on revient sur le scan de ref
                self.mode = "user"
                self.ui.scanDone.emit(self.user.matricule)
            elif self.mode == "qualite":
                self.IOHandler.deActivateActuator()
                #ASMA
                self.refHandler.nb=0 
                self.updateUI.emit()
                self.userHandler.log("verin desactive pour cause qualite")


    # Si nous avons une erreur série, il faut la mettre ici
    @QtCore.pyqtSlot(str)
    def serialError(self, message):
        if self.mode == "test" or self.mode == "sendTest" or self.mode == "runningtest" or self.mode == "default":
            self.mode = "error"
            logging.debug(message)
            self.ui.setInfoWindow(message , QtCore.Qt.red)


""" Main Functions """
def main():
    # obscure reason
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    # Lecture du fichier conf
    aConfigHandler = configHandler("conf/test.conf")
    # configure les logs
    # le fichier aura le nom du temps UNIX
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    logFileName = configHandler.logDirectory + str(time.time()) + '.log'
    logging.basicConfig(filename=logFileName, format=FORMAT, datefmt='%d/%m/%Y %H:%M:%S', level=logging.DEBUG)

    logging.info('Lancement du programme')

    app = QtGui.QApplication(sys.argv)
    evHa = eventHandler(aConfigHandler)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

