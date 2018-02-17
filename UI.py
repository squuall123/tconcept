# -*- coding: utf-8 -*-

"""
Python interface pour tconcept
    author: Baptiste Denaeyer
"""

import sys, csv, logging,ConfigParser
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QObject, QThread
from PyQt4.QtGui import QAction, QKeySequence, QVBoxLayout, QHBoxLayout, QBoxLayout, QPainter
from PyQt4.QtGui import *
from configHandler import *
from userHandler import *
from refHandler import *
from printHandler import *
from serialComHandler import *

class UI(QtGui.QWidget):
    # Definition des signaux
    scanDone = QtCore.pyqtSignal(str)
    buttonPressed = QtCore.pyqtSignal(str)
    testFaisceau = QtCore.pyqtSignal(int)
    configHandler = ""
    debug = False
    timeout = 0
    etanche1=0
    IOHandler = None
    user = ""
	

    def __init__(self, configHandler, IOHandler):
        super(UI, self).__init__()
        self.configHandler = configHandler
        self.initUI()
        self.IOHandler = IOHandler
        self.refHandler= refHandler
        self.serialHandler = serialComHandler(self.configHandler)
     
        
    def paintEvent(self, e):
        # Test cercle rouge:
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)
        radx = 10
        rady = 10
        # Dessine les ronds pour les tests
        paint.setPen(QtCore.Qt.black)
        # Reseau
        center = QtCore.QPoint(20, 20)
        if self.startTest == 0:
            paint.setBrush(QtCore.Qt.red)
        elif self.startTest > 0:
            paint.setBrush(QtCore.Qt.green)

        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(36,26), u"Connexion réseau")
        
        # Carte
        if self.startTest > 1:
            paint.setBrush(QtCore.Qt.green)
        elif self.startTest == 1:
            paint.setBrush(QtCore.Qt.red)
        elif self.startTest < 1:
            paint.setBrush(QtGui.QColor(0,0,0, 0))
        center = QtCore.QPoint(20, 50)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(36,56), u"Connexion carte")
        
        # Imprimante
        if self.startTest > 2:
            paint.setBrush(QtCore.Qt.green)
        elif self.startTest == 2:
            paint.setBrush(QtCore.Qt.red)
        elif self.startTest < 2:
            paint.setBrush(QtGui.QColor(0,0,0, 0))
        center = QtCore.QPoint(20, 80)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(36,86), u"Présence imprimante")
        
        # Air
        if self.IOHandler.aircomprime == 1:
            paint.setBrush(QtCore.Qt.green)
        elif  self.IOHandler.aircomprime == 0:
            paint.setBrush(QtCore.Qt.red)
        elif  self.IOHandler.aircomprime == -1:
            paint.setBrush(QtGui.QColor(0,0,0, 0))
        center = QtCore.QPoint(300, 20)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(316,26), u"Présence air comprimé")

        # Ticket
        if self.IOHandler.etiquette == 1:
            paint.setBrush(QtCore.Qt.green)
        elif  self.IOHandler.etiquette == 0:
            paint.setBrush(QtCore.Qt.red)
        center = QtCore.QPoint(300, 50)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(316,56), u"Présence étiquette")
        
        # Faisceau
        if self.IOHandler.faisceau == 1:
            paint.setBrush(QtCore.Qt.green)
        elif  self.IOHandler.faisceau == 0:
            paint.setBrush(QtCore.Qt.red)
        center = QtCore.QPoint(300, 80)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(316,86), u"Présence faisceau")
        
        # Verin
        if self.IOHandler.verin == 1:
            paint.setBrush(QtCore.Qt.green)
        elif  self.IOHandler.verin == 0:
            paint.setBrush(QtCore.Qt.red)
        center = QtCore.QPoint(510, 20)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(526,26), u"Verrouillage faisceau")
        
          #asma
        # Etancheite
        
        
        if self.etanche1==1:
            paint.setBrush(QtCore.Qt.green)
        elif  self.etanche1 == 0:
			paint.setBrush(QtCore.Qt.red)
 
        center = QtCore.QPoint(510, 50)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(526,56), u"Etanchéité")
        
       
       
		
        
        # Info
        #if self.IOHandler.verin == 1:
        #    paint.setBrush(QtCore.Qt.green)
        #elif  self.IOHandler.verin == 0:
        paint.setBrush(QtCore.Qt.red)
        center = QtCore.QPoint(510, 80)
        paint.drawEllipse(center, radx, rady)
        paint.drawText(QtCore.QPoint(526,86), u"Info")

        paint.drawText(QtCore.QPoint(516,116), self.user)

        paint.end()

    @QtCore.pyqtSlot()
    def updateUI(self):
        self.update()

    def initUI(self):
	self.debugLayout = QHBoxLayout()
        self.layout = QVBoxLayout()
	self.debugLayout.addLayout(self.layout)

	# Si on est en mode debug, on affiche les logs
        if self.configHandler.debug:
            self.showLog()

        # Date and Time
        self.timeLabel = QtGui.QLabel(QtCore.QDateTime.currentDateTime().toString())
        self.timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.dateUpdate)
        self.timer.start(1000)
        self.layout.setDirection(QBoxLayout.BottomToTop)
        self.layout.addWidget(self.timeLabel)


        # Mettre le style du Titre
        self.font = QtGui.QFont()
        self.font.setPointSize(30)
        self.palette = QtGui.QPalette()
        self.title = QtGui.QLabel()


        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setFont(self.font)
        self.title.setPalette(self.palette)

        # Mettre le style de la table
        self.paletteTable = QtGui.QPalette()
        self.table = QtGui.QLabel()
        self.table.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        self.table.setFixedHeight(160)
        self.table.setFont(self.font)
        self.paletteTable.setColor(QtGui.QPalette.Foreground, QtGui.QColor(0x3C, 0xA7, 0x87))
        self.table.setPalette(self.paletteTable)
        self.table.setText(u"Table de contrôle N°: " + self.configHandler.numTable)

        # Un label pour le nom du programme
        self.paletteProgName = QtGui.QPalette()
        self.progName = QtGui.QLabel()
        self.progName.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
        #self.progName.setFixedHeight(160)
        self.progName.setFont(self.font)
        self.paletteProgName.setColor(QtGui.QPalette.Foreground, QtGui.QColor(50, 0, 230))
        self.progName.setPalette(self.paletteProgName)
        self.progName.hide()
        
        #label pour asma

        #self.label1 = QtGui.QLabel()
      
 
       


        # Label por le scan
        self.font2 = QtGui.QFont()
        self.font2.setPointSize(20)
        self.aLabel = QtGui.QLabel()

        self.aLabel.setFont(self.font2)
        

       
    

        # Espace pour scan
        self.scanEdit = QtGui.QLineEdit()
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(20)
        self.grid.addWidget(self.aLabel, 1, 0)
        #label pour asma 
        #self.grid.addWidget(self.label1, 1, 0)
        #self.font3= QtGui.QFont()
        #self.font3.setPointSize(30)
        #self.label1.setFont(self.font2)
        
        
     
       
        self.grid.addWidget(self.scanEdit, 1, 1)
        self.grid.setContentsMargins(30,30,30,30)


        # Compteur de piece bonnes
        self.countFrame = QtGui.QFrame()
        self.countGoodTextLabel = QtGui.QLabel()
        self.countWrongTextLabel = QtGui.QLabel()
        self.countGoodLabel = QtGui.QLabel()
        self.countWrongLabel = QtGui.QLabel()
        self.countGrid = QtGui.QGridLayout(self.countFrame)
        self.countGrid.setSpacing(10)
        self.countTextFont = QtGui.QFont()
        self.countTextFont.setPointSize(30)
        self.countGoodTextPalette = QtGui.QPalette()
        self.countGoodTextPalette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(0x00, 0xFF, 0x00))
        self.countWrongTextPalette = QtGui.QPalette()
        self.countWrongTextPalette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(0xFF, 0x00, 0x00))
        self.countGoodTextLabel.setText(u"Compteur\npièces bonnes")
        self.countGoodTextLabel.setFont(self.countTextFont)
        self.countGoodTextLabel.setPalette(self.countGoodTextPalette)
        self.countGoodTextLabel.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        self.countWrongTextLabel.setText(u"Compteur\npièces mauvaises")
        self.countWrongTextLabel.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        self.countWrongTextLabel.setFont(self.countTextFont)
        self.countWrongTextLabel.setPalette(self.countWrongTextPalette)
        self.countGoodLabel.setText(u"0000")
        self.countGoodLabel.setFont(self.countTextFont)
        self.countGoodLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.countGoodLabel.setPalette(self.countGoodTextPalette)
        self.countWrongLabel.setText(u"0000")
        self.countWrongLabel.setFont(self.countTextFont)
        self.countWrongLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.countWrongLabel.setPalette(self.countWrongTextPalette)
        self.countGrid.addWidget(self.countGoodTextLabel, 0, 0)
        self.countGrid.addWidget(self.countGoodLabel, 1, 0)
        self.countGrid.addWidget(self.countWrongTextLabel, 0, 1)
        self.countGrid.addWidget(self.countWrongLabel, 1, 1)
        self.countGrid.setContentsMargins(10,30,10,10)
        self.countFrame.hide()
        

        # Temps passé a tester
        self.timeFrame = QtGui.QFrame()
        self.elapsedTimeTextLabel = QtGui.QLabel()
        self.bestTimeTextLabel = QtGui.QLabel()
        self.elapsedTimeLabel = QtGui.QLabel()
        self.bestTimeLabel = QtGui.QLabel()
        self.timeGrid = QtGui.QGridLayout(self.timeFrame)
        self.timeGrid.setSpacing(10)
        self.timeTextFont = QtGui.QFont()
        self.timeTextFont.setPointSize(30)
        self.timeTextPalette = QtGui.QPalette()
        self.timeTextPalette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(0xA7, 0x78, 0x34))
        self.elapsedTimeTextLabel.setText(u"Temps écoulé")
        self.elapsedTimeTextLabel.setFont(self.timeTextFont)
        self.elapsedTimeTextLabel.setPalette(self.timeTextPalette)
        self.bestTimeTextLabel.setText(u"Meilleur temps")
        self.bestTimeTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.bestTimeTextLabel.setFont(self.timeTextFont)
        self.bestTimeTextLabel.setPalette(self.timeTextPalette)
        self.elapsedTimeLabel.setText(u"00:00")
        self.elapsedTimeLabel.setFont(self.timeTextFont)
        self.bestTimeLabel.setText(u"00:00")
        self.bestTimeLabel.setFont(self.timeTextFont)
        self.bestTimeLabel.setAlignment(QtCore.Qt.AlignRight)
        self.timeGrid.addWidget(self.elapsedTimeTextLabel, 1, 0)
        self.timeGrid.addWidget(self.elapsedTimeLabel, 2, 0)
        self.timeGrid.addWidget(self.bestTimeTextLabel, 1, 1)
        self.timeGrid.addWidget(self.bestTimeLabel, 2, 1)
        self.timeGrid.setContentsMargins(10,10,10,10)
        self.timeFrame.hide()
       

        # Test d'étanchéité
        

        self.layout.addWidget(self.countFrame)
        self.layout.addWidget(self.timeFrame)
        self.layout.addLayout(self.grid)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.progName)
        self.layout.addWidget(self.table)
        self.scanEdit.setFont(self.font2)
        self.scanEdit.returnPressed.connect(self.sendScan)
 

        self.scanEdit.setText("")
        self.scanEdit.setFocus()

        # Raccourcie <ctrl>+<Q> -> quit (juste pour le dev ...)
        self.actionExit = QAction(('E&xit'), self)
        self.actionExit.setShortcut(QKeySequence("Ctrl+Q"))
        self.addAction(self.actionExit)
        self.actionExit.triggered.connect(self.close)
        
        # test Timer
        self.testTimer=QtCore.QTimer(self)
        self.testTimer.timeout.connect(self.testTimerUpdate)

        self.setLayout(self.debugLayout)

        #self.resize(600, 600)
	self.showFullScreen()
        self.show()

    # Juste pour le debug.
    # Si 'q' est appuyé, on quit et on relance l'appli
    # Si 'p' est appuyé, on simule un appuis de bouton
    def keyPressEvent(self, event):
        if event.text() == 'p':
            self.buttonPressed.emit('START')
        elif event.text() == 'q':
            self.buttonPressed.emit('CANCEL')

    # Affiche le nom du programme en cours de test
    def showProgName(self, progName):
        self.progName.setText(progName)
        self.progName.show()

    # On lance le test avec les affichages qui vont bien
    def startTimeAndCount(self, faisceauTimeout):
        self.faisceauTimeout = faisceauTimeout
        self.timeElapsed = 0
        self.timeFrame.show()
        self.countFrame.show()
        self.startTestTime = QtCore.QDateTime.currentDateTime()
        self.testTimer.start(200)
       
    # Reset le timer en cas de nouvelle pièce par exemple
    def resetTimer(self):
        self.startTestTime = QtCore.QDateTime.currentDateTime()

    def stopTimer(self):
        self.testTimer.stop()

    def updateBestTime(self, newBestTime):
        newBestTimeText = "%02d:" % (newBestTime/60)
        newBestTimeText += "%02d" % (newBestTime%60)
        self.bestTimeLabel.setText(newBestTimeText)


    # Le timer de test
    def testTimerUpdate(self):
        now = QtCore.QDateTime.currentDateTime()
        self.timeElapsed = -now.secsTo(self.startTestTime)
        timeElapsedText = "%02d:" % (self.timeElapsed/60)
        timeElapsedText += "%02d" % (self.timeElapsed%60)
        self.elapsedTimeLabel.setText(timeElapsedText)
        if self.faisceauTimeout != 0:
            self.testFaisceau.emit(self.timeElapsed)

    # Fonction permettant d'afficher les compteurs
    def displayGoodCounter(self, counter):
        counterText = "%04d" % counter
        self.countGoodLabel.setText(counterText)

    # Fonction permettant d'afficher les compteurs
    def displayWrongCounter(self, counter):
        counterText = "%04d" % counter
        self.countWrongLabel.setText(counterText)

    # On affiche les logs à la demande
    def showLog(self):
        if not self.debug:
            # Composant python qui gere l'update des logs comme un grand
            self.logHandler = QtGui.QTextEdit()
            self.setStyleSheet("QTextEdit{background-color:back;}")
            self.logHandler.setTextColor(QtCore.Qt.white)
            self.logHandler.setReadOnly(True)
            self.logHandler.setFixedWidth(500)
            self.debugLayout.addWidget(self.logHandler)
            self.debug = True
        else: 
            self.logHandler.show()

    # On cache les logs à la demande
    def hideLog(self):
        if self.debug:
            self.logHandler.hide()
            self.debug = True
    
    def dateUpdate(self):
        try:
            # Timer qui update l'heure toute les secondes
            self.timeLabel.setText(QtCore.QDateTime.currentDateTime().toString())
	    with open(logging.getLoggerClass().root.handlers[0].baseFilename, 'r') as content_file:
                content = content_file.read()
        	if self.debug:
                    self.logHandler.setPlainText(content)
                    self.logHandler.moveCursor(QtGui.QTextCursor.End)

        except KeyboardInterrupt:
	    self.close()



    def sendScan(self):
        # transmet le texte saisie au main
        text = self.scanEdit.text()
        logging.info(u'Scan effectué:  ' + text )
        self.scanDone.emit(text)
	

    def setInfoWindow(self, title, color):

        self.setFocus()
        self.scanEdit.hide()
        self.aLabel.hide()
        
   



        # Mettre le style du Titre
        self.palette.setColor(QtGui.QPalette.Foreground, color)
        self.title.setPalette(self.palette)
        self.title.setText(title)
        self.setWindowTitle(title)
    #def sett(self,label,color):
		

        #self.label1.setFixedSize(150,150)
       
        #self.setFocus()
       # self.label1.setText(label)
        #self.palette.setColor(QtGui.QPalette.Foreground, color)
        #self.label1.setPalette(self.palette)
        #self.label1.show()
        
       
    @QtCore.pyqtSlot(str, str, QtGui.QColor)
    def setScanWindow(self, title, label, color):
        # Mettre le style du Titre
        self.palette.setColor(QtGui.QPalette.Foreground, color)
        self.title.setPalette(self.palette)
        self.title.setText(title)
        self.setWindowTitle(title)
        


        self.aLabel.setText(label)

        
        self.scanEdit.show()
        self.aLabel.show()
        self.scanEdit.setText("")
        self.scanEdit.setFocus()
        

 


    def refWindow(self, name, error=""):
        if error == "":
            # Dire bonjour à l'utilisateur
            self.setScanWindow('Bonjour ' + name, u'Veuillez scanner une référence de faisceau', QtCore.Qt.blue)
        else:
            # Afficher l'erreur
            self.setScanWindow(error, u'Veuillez présenter une nouvelle référence', QtCore.Qt.red)
	

    def userWindow(self, error = ""):
        self.hideLog()
        if error == "":
            self.setScanWindow('Bonjour', 'Veuillez scanner votre matricule', QtCore.Qt.blue)
         
        else:
            # Affiche l'erreur en rouge
            self.setScanWindow(error, 'Veuillez scanner votre matricule', QtCore.Qt.red)

		
    @QtCore.pyqtSlot()
    def returnToUser(self):
        self.resetTimer()
        self.stopTimer()
        self.userWindow()
        self.timeFrame.hide()
        self.countFrame.hide()
        self.progName.hide()

    
    @QtCore.pyqtSlot(str)
    def returnToRef(self, name):
        self.resetTimer()
        self.stopTimer()
        self.refWindow(name)
        self.timeFrame.hide()
        self.countFrame.hide()
        self.progName.hide()

