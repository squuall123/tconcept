# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import sys, logging, serial, time
from configHandler import *
from userHandler import *
from refHandler import *

class SerialError(Exception):
    pass

class TestError(Exception):
    pass

class serialComHandler:
    errorFlag = False
    timeout = 0
    etanchiete1=0
 

    def __init__(self, configHandler):
        try:
            self.timeout = configHandler.serialTimeout
            # initialise la communication série
            self.ser = serial.Serial(configHandler.serialPort, configHandler.serialBaud, timeout=configHandler.serialTimeout)
            #self.ser.setDTR(False)
            if self.ser.isOpen() == False:
                raise SerialError("Le port serie n'est pas ouvert")
            self.errorFlag = False
            # Reset de tout le port série avant de faire quoi que ce soit
            self.ser.flushInput()
            self.ser.flushOutput()
            #ASMA ETANCHIETE
            
            
            #self.etanchiete1=self.refHandler.refConfig.etanchiete 
            #self.ser.reset_input_buffer()
            #self.ser.reset_output_buffer()
        except serial.SerialException, e:
            raise SerialError(e)
        except OSError as e:
            raise SerialError(e.strerror)

# Commande de la carte

    # Vide la liste précédente
    def sendIT(self):
        buf = [0XCE]
        if self.sendCommand(buf):
            logging.info("IT: Liste vide dans le controleur ")

    # DÃ©finie courant de test
    def sendCT(self, value):
        valueH = value >> 8
        valueL = value - valueH * 0x100

        buf = [0x11, valueH, valueL]
        if self.sendCommand(buf):
            logging.info("CT emis")

    # Définie le seuil de continuitÃ©
    def sendSC(self, value):
        valueH = value >> 8
        valueL = value - valueH * 0x100

        buf = [0x7C, valueH, valueL]
        if self.sendCommand(buf):
            logging.info("SC: emis")
            
    def Desactivelectrovane2(self):
		self.sendES(0x01,0x00)
            
    def Desactivelectrovane1(self):
		self.sendES(0x09,0x00)
		
            
    def Active2(self):
		self.sendES(0x0D,0x00)

    # Envois d'un point de continuitÃ©
    # pour le listing de point
    # pour 2 points seulement


    def sendPC_2(self, valueA, valueB):
        valueAH = valueA >> 8
        valueAL = valueA - valueAH * 0x100
        valueBH = valueB >> 8
        valueBL = valueB - valueAH * 0x100

        buf=[0xC7, 0x04, valueAH, valueAL, valueBH, valueBL]
        if self.sendCommand(buf):
            logging.info("PC_2: emis")
            
            #ASMA POINT ISOLÉ
    def sendPNC_2(self, valueA, valueB):
		valueAH = valueA >> 8
		valueAL = valueA - valueAH * 0x100
		valueBH = valueB >> 8
		valueBL = valueB - valueAH * 0x100
		buf=[0x17, valueAH, valueAL, valueBH, valueBL]
		print "liste"
		print buf
		if self.sendliste(buf):
			logging.info("PNC_2: emis")
		
	
	
    # Envoi le start du test
    def sendTC(self, command):
        buf=[0xC5, command]
        if self.sendCommand(buf):
            logging.info("TC: start Test emis")
           
           
           #ASMA TEST POINT ISOLÉ START 
    def sendTNC(self, command):
		buf=[0x15, command]
		print"start"
		print buf
		if self.sendliste(buf):
			logging.info("TNC: start Test point isolé emis")
			print "TNC: start Test point isolé emis"
		


    # Demande etat des sortie
    def sendEE(self):
        buf = [0xE0]
        logging.info("Etat des entrees demandes")
        return  self.sendRequest(buf)
        #asma
    def sendEA(self,byte):
		buf = [0xEA,byte]
		logging.info("Etat des entrees analogic demandes")
		return self.sendRequest(buf)
         #asma
   # def sende(self, byte1, byte2):
	#	buf=[0xE1, byte1, byte2]
	#	if self.sendCommand(buf):
	#		logging.info("Sorties commandees à l'etat " + str(byte1) + str(byte1))

    # Active des sorties
    
    def sendANA(self ,byte1,byte2):
		buf = [0x5A,byte1,byte2]
		if  self.sendCommand(buf):
			logging.info("Sorties commandees analogic à l'etat " + str(byte1) + str(byte1))

		
    def sendES(self, byte1, byte2):
        buf=[0xEF, byte1, byte2]
        if self.sendCommand(buf):
            logging.info("Sorties commandees à l'etat " + str(byte1) + str(byte1))



    # Allume les leds
    def lightLED(self, point_led):
        buf = [0xA1, 0x00, point_led, 0x01]
        if self.sendCommand1(buf) and point_led != 0:
           logging.info("LED " +str( point_led ) + " active")
           
	

	
		
				
#asma activer electrovanne 1      
    def Activelectrovane1(self):
		self.sendES(0x05,0x00)
	
			
    # eteinds toute les leds
    def turnOffLED(self):
        buf =[0xA1, 0xFF, 0xFF, 0x00]
        if self.sendCommand1(buf):
            logging.info("eteinte de toutes les LEDs")
            
	
	
    

    # mode sonde
    def sendPS(self, state):
        buf = [0x57, state]
        if self.sendCommand(buf):
            logging.info("Changement du mode sonde: " + str(state))
            
            


    def cancelTest(self):
        buf = [0xC5, 0x50]
        if self.sendCommand(buf):
            logging.info("Annulation du test emis a la carte")
            
            #asma modif
    def buzzerof(self):
		self.sendES(0x01, 0x00)
            #asma modif
    def buzzeron(self):
		self.sendES(0x03,0x00)
	
	

	

# Commande générale

    def checkSum(self, buf):
        if type(buf) is list:
            aSum = 0
            for char in buf:
                aSum += char
            aSum = aSum % 0x100
            aSum = (0x100 - aSum) % 0X100
            # TODO: Useless?
            if aSum == 0x100:
                aSum = 0x00
            return aSum
        else:
             return 0

    def checkCheckSum(self, buf):
        newBuf = buf[:]
        newBuf.pop()
        return buf[len(buf)-1] == self.checkSum(newBuf)
        
    #ASMA POINT ISOLÉ
    
    def sendliste(self,buf, timeout=-1):
		if timeout == -1:
			self.ser.timeout = self.timeout 
		else:
			self.ser.timeout = timeout
	
		if self.ser.isOpen() == False:
			raise SerialError("Le port serie n'est pas ouvert")
		for char in buf:
			self.ser.write(chr(char))
		self.ser.write(chr(self.checkSum(buf)))
		logging.info( ':'.join([ "%02X " %  x  for x in buf ] ).strip())
		self.ser.flush()
		char = self.ser.read()
		if len(char) != 0:
			rBuf = [int(ord(char))]
			while  self.checkCheckSum(rBuf) == False:
				char = self.ser.read()
				if  len(char) != 0:
					rBuf.append(int(ord(char)))
					print "reponse start test list"
					print rBuf
				else:
					if self.errorFlag:
						self.errorFlag = False
						raise SerialError("Erreur d'envoie: backTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
					else:
						print "renvoie commande"
						self.errorFlag = True
						self.sendCommand(buf)
			logging.info('Recu après envoie ' + ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
			if rBuf[0] == 0x17 and rBuf [1] == 0x00:
				raise SerialError("Erreur de programmation de la carte")
			return True
		else :
			raise SerialError("Aucune reponse de la carte")	
			
			
    def sendCommand1(self, buf, timeout=-1):
		if timeout == -1:
			self.ser.timeout= self.timeout
		else:
			self.ser.timeout = timeout
		if self.ser.isOpen() == False:
			raise  SerialError("Le port serie n'est pas ouvert")
		for char in buf:
			self.ser.write(chr(char))
		self.ser.write(chr(self.checkSum(buf)))
		logging.info( ':'.join([ "%02X " %  x  for x in buf ] ).strip())
		self.ser.flush()
		print buf
		return  True
				
		
							
				
  

		


    def sendCommand(self, buf, timeout=-1):
        if timeout == -1:
            self.ser.timeout = self.timeout 
        else:
            self.ser.timeout = timeout
        if self.ser.isOpen() == False:
            raise SerialError("Le port serie n'est pas ouvert")
        # envoie du buffer
        for char in buf:
            self.ser.write(chr(char))
        # Envoie checksum
        self.ser.write(chr(self.checkSum(buf)))
        logging.info( ':'.join([ "%02X " %  x  for x in buf ] ).strip())
        self.ser.flush()

        # La commande est envoyé on attends pour la rÃ©ponse
        # On s'arrête quand le checksum est bon
        char = self.ser.read()
       

        if len(char) != 0:
            rBuf = [int(ord(char))]
            while self.checkCheckSum(rBuf) == False:
                char = self.ser.read()
              
                if len(char) != 0:
                    rBuf.append(int(ord(char)))
                else:
                    if self.errorFlag:
                        self.errorFlag = False
                        raise SerialError("Erreur d'envoie: backTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
                    else:
                        #Renvoie une fois si il y a une erreur quelconque
                        print "renvoie commande"
                        self.errorFlag = True
                        self.sendCommand(buf)

            logging.info('Recu après envoie ' + ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            if rBuf[0] == 0xC7 and rBuf [1] == 0x00:
                raise SerialError("Erreur de programmation de la carte")
            return True
        else:
            raise SerialError("Aucune reponse de la carte")

    def sendRequest(self, buf, timeout = -1):
        if self.ser.isOpen() == False:
            raise SerialError("Le port serie n'est pas ouvert")
        if timeout == -1:
            self.ser.timeout = self.timeout 
        else:
            self.ser.timeout = timeout
        # envoie du buffer
        for char in buf:
            self.ser.write(chr(char))
        # Envoie checksum
        self.ser.write(chr(self.checkSum(buf)))
        logging.info( ':'.join([ "%02X " %  x  for x in buf ] ).strip())
        logging.info('Checksum: ' + "%02X " % self.checkSum(buf))
        self.ser.flush()
        
        # Attente de la réponse multiple
        char = self.ser.read()
        
        if len(char) != 0:
            rBuf = [int(ord(char))]
            logging.info( ':'.join([ "%02X " %  x  for x in buf ] ).strip())
            while self.checkCheckSum(rBuf) == False:
                char = self.ser.read()
                if len(char) != 0:
                    rBuf.append(int(ord(char)))
                else:
                    raise SerialError("Aucune reponse de la carte\nOu erreur de checksum\nBackTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            return rBuf
            


    def read(self):
        nbByte = self.ser.inWaiting()
        if nbByte > 0:
            buf = self.ser.read(nbByte)
            if checkCheckSum(buf):
                return buf
            else:
                raise SerialError("CheckSum incorrect")
        else :
            raise SerialError("Aucun actect à lire sur la ligne")
        return None


    def waitSondeResponse(self):
        timeout = self.ser.timeout
        self.ser.timeout = 0
        char = self.ser.read()
        if len(char) != 0:
            rBuf = [int(ord(char))]
            while self.checkCheckSum(rBuf) == False:
                char = self.ser.read()
                if len(char) != 0:
                    rBuf.append(int(ord(char)))
                    print "rep"
                    print rBuf
                else:
                    self.ser.timeout = timeout
                    raise SerialError("Aucune reponse de la carte\nOu erreur de checksum\nBackTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            logging.info( "Response apres test "+':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            if 0x57 == rBuf[0]:
                # point de sonde trouvé
                self.ser.timeout = timeout
                return rBuf[1] * 0x100 + rBuf[2]
        self.ser.timeout = timeout
        
        #ASMA TEST POINT ISOLÉ
  

    def waitTestResponse(self):
        timeout = self.ser.timeout
        self.ser.timeout = 0
        char = self.ser.read()
        if len(char) != 0:
            rBuf = [int(ord(char))]
            while self.checkCheckSum(rBuf) == False:
                char = self.ser.read()
                if len(char) != 0:
                    rBuf.append(int(ord(char)))
              
                else:
                    self.ser.timeout = timeout
                    raise SerialError("Aucune reponse de la carte\nOu erreur de checksum\nBackTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            logging.info( "Response apres test elec "+':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
            print rBuf
            if [0xC5, 0xF1] == rBuf[0:2]:
                print "TEST OK"
                # Test was ok !
                self.ser.timeout = timeout
                return [0x00];
            elif [0xC5, 0xDC] == rBuf[0:2]:
                # erreur: pas de liste dans la carte
                return [0xDC]
            elif [0xC5, 0xD0] == rBuf[0:2]:
                # Coupure sur les deux prochains points
                print rBuf[1:6]
                self.ser.timeout = timeout
                return rBuf[1:6]
            #elif [0xC5, 0xD7]== rBuf[0:2]:
				#print rBuf[1:6]
				#print "hors tolerance"
				#self.ser.timeout = timeout
				#return rBuf[1:6] 
            elif [0x15,0xF1]==rBuf[0:2]:
				return rBuf[0:2]
				print"test point isolt ok"

            elif [0xC5, 0xDF] == rBuf[0:2]:
                # Court circuit les deux prochains points
                print rBuf[1:6]
                self.ser.timeout = timeout
                return rBuf[1:6]
            elif [0x17, 0xDC] == rBuf[0:2]:
				return rBuf[0:2]
            elif [0x17, 0xD0] == rBuf[0:2]:
				return rBuf[0:6]
            elif [0x17, 0xDF] == rBuf[0:2]:
				return rBuf[0:6]
            elif  [0x17,0xF1] == rBuf[0:2]:
				print "TEST point isolé OK"
				return rBuf[0:2]
				print rBuf[0:2]

			

	
			
    
           
    def w(self):
		timeout = self.ser.timeout
		self.ser.timeout = 0
		char = self.ser.read()
		if len(char) != 0:
			rBuf = [int(ord(char))]
			print "rep"
			print rBuf
			while self.checkCheckSum(rBuf) == False:
				char = self.ser.read()
				if len(char) != 0:
					rBuf.append(int(ord(char)))
					print"rep2"
					print rBuf
				else:
					self.ser.timeout = timeout
					raise SerialError("Aucune reponse de la carte\nOu erreur de checksum\nBackTrace: "+ ':'.join([ "%02X " %  x  for x in rBuf ] ).strip())

			logging.info( "Response apres test point isol  "+':'.join([ "%02X " %  x  for x in rBuf ] ).strip())
			if [0x15,0xF1] == rBuf[0:2]:
				print "TEST point isolé OK"
			
				return rBuf;
			elif [0x17, 0xDC] == rBuf[0:2]:
				return [0xDC]
			elif [0x17, 0xD0] == rBuf[0:2]:
				#print rBuf
				return rBuf[1:6]
			elif [0x17, 0xDF] == rBuf[0:2]:
				return rBuf[1:6]
				#print "defaut"
				#print rBuf[1:6]
			else:
				return rBuf
			
		

