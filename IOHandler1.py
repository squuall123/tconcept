# -*- coding: utf-8 -*-

"""
AirTank Handler pour tconcept
    author: Baptiste Denaeyer
"""

import logging,ConfigParser
import RPi.GPIO as GPIO
from serialComHandler import *
from configHandler import *
from refHandler import *

class IOHandler:

    aircomprime = -1
    faisceau = 0
    etiquette = 0
    verin = 0
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
  


    def __init__(self, serialHandler, callback):
        self.callback = callback
        self.serialHandler = serialHandler
        self.eventPin = 18
        self.startPin = 25
        self.cancelPin = 6
        self.faisceauPin = 26
        self.etiquettePin = 12
        #VERRIN
        self.redPin = 21
        self.orangePin = 23 
        self.greenPin = 24
        GPIO.setmode(GPIO.BCM)
        # C'est donc bien une entrée
        GPIO.setup(self.eventPin,GPIO.IN)
        #GPIO.setup(self.eventPin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.startPin,GPIO.IN)
        GPIO.setup(self.cancelPin,GPIO.IN)
        GPIO.setup(self.faisceauPin,GPIO.IN)
        GPIO.setup(self.etiquettePin,GPIO.IN)
        
        # VERRIN
        GPIO.setup(self.redPin,GPIO.OUT)
        GPIO.setup(self.orangePin,GPIO.OUT)
        GPIO.setup(self.greenPin,GPIO.OUT)
        self.faisceau = not GPIO.input(self.faisceauPin)
        self.etiquette = not GPIO.input(self.etiquettePin)
        GPIO.add_event_detect(self.eventPin, GPIO.RISING, callback=self.event, bouncetime=1)
        GPIO.add_event_detect(self.startPin, GPIO.RISING, callback=self.event, bouncetime=100)
        GPIO.add_event_detect(self.cancelPin, GPIO.RISING, callback=self.event, bouncetime=100)
        GPIO.add_event_detect(self.faisceauPin, GPIO.BOTH, callback=self.event, bouncetime=1)
        GPIO.add_event_detect(self.etiquettePin, GPIO.BOTH, callback=self.event, bouncetime=1)
        #asma
       

    def event(self, eventPin):
        print "-- An Event Occured -- %s" % eventPin
        # buf = self.serialHandler.read()
        if eventPin == self.eventPin:
            buf = self.serialHandler.sendEE()
            if buf != None:
                print buf
                if buf[0] == 0xE0 and len(buf) == 4:
                    cardInput = buf[2] * 0x100 + buf[1]
                    print cardInput
                    if(cardInput & 0b10) == 0b10:
                        # On a détecté de l'air comprimé !
                        # signalons le !
                        self.aircomprime = 1
                    else:
                        self.aircomprime = 0
                    if(cardInput & 0b1) == 0b1:
                        # On a détecté le faisceau !
                        # signalons le !
                        self.faisceau = 1
                    else:
                        self.faisceau = 0
                    if(cardInput & 0b100) == 0b100:
                        # On a détecté l'étiquette !
                        # signalons le !
                        self.etiquette = 1
                    else:
                        self.etiquette = 0
                    self.callback("INPUTS")
        elif eventPin == self.startPin:
            # On a appuyé sur start
            self.callback("START")
        elif eventPin == self.cancelPin:
            # On a appuyé sur cancel
            self.callback("CANCEL")
        elif eventPin == self.faisceauPin:
            # Présence faisceau
            self.faisceau = not GPIO.input(self.faisceauPin)
            self.callback("INPUTS")
        
        elif eventPin == self.etiquettePin:
            # Presence etiquette
            self.etiquette = not GPIO.input(self.etiquettePin)
            self.callback("INPUTS")


     
     
    def testEA(self, byte):
        try:
            rBuf = self.serialHandler.sendEA(byte)
            print rBuf
            if rBuf == None:
                return False
            if rBuf[0] == 0xEA:
                cardInput1 = rBuf[2] * 0x100 + rBuf[3]
                print cardInput1
                return cardInput1
            else:
                return False
        except SerialError as e:
            logging.debug(u"Erreur de test des entrees de la carte" + e.message)
            return False
        

    # test un entrée spécifique grâce au mask
    def testEE(self, mask):
        try:
            rBuf = self.serialHandler.sendEE()
            print rBuf
            if rBuf == None:
                return False
            if rBuf[0] == 0xE0:
                cardInput = rBuf[2] * 0x100 + rBuf[1]
                return (cardInput & mask) == mask
            else:
                return False
        except SerialError as e:
            logging.debug(u"Erreur de test des entrees de la carte" + e.message)
            return False
            #ASMA
      
      

		
		

       
	
    def testAirPressure(self):
        # pour le test de l'air comprimé on prend le bit 2
        test = self.testEE(0b10)
        print test
        if test:
            self.aircomprime = 1
        else:
            self.aircomprime = 0
        return test

    # Verifie la présence d'un faisceau
    def testFaisceau(self):
		test = self.testEE(0b1)
		print test
		if test:
			 self.faisceau = 1
		else:
			self.faisceau= 0
		return test

    # Vérifie la précense d'un ticket
    """def testTicket(self):
        return self.testEE(0b100)"""
    
    # Active le verin
    def activateActuator(self):
        # le vérin est à la sortie 0
        self.serialHandler.sendES(0x01, 0x00)
        self.verin = 1
    
    # Desactive le verin
    def deActivateActuator(self):
        # le vérin est à la sortie 0
        self.serialHandler.sendES(0x00, 0x00)
        self.verin = 0  

   
   
    def checkSonde(self):
        rbuf = self.serialHandler.waitSondeResponse()
        if rbuf != None:
            return rbuf
            
    def verrin(self, state):
        if state == "red":
            GPIO.output(self.redPin, 1)
            GPIO.output(self.orangePin, 0)
            GPIO.output(self.greenPin, 0)
        if state == "orange":
            GPIO.output(self.redPin, 0)
            GPIO.output(self.orangePin, 1)
            GPIO.output(self.greenPin, 0)
        if state == "green":
            GPIO.output(self.redPin, 0)
            GPIO.output(self.orangePin, 0)
            GPIO.output(self.greenPin, 1)

