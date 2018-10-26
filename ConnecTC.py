#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QFrame, QVBoxLayout
import FFT_Magnitude.core as FFTMag

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument



class ConneTC_GUI(QMainWindow):

    instrumentList = []

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.ex = HorizontalBox()
        self.setCentralWidget(self.ex)

        self.statusBar()

        ConnectBtn = QPushButton("Conectar", self.ex.rightFrame)
        ConnectBtn.resize (80,30)
        ConnectBtn.clicked.connect(self.connectButtonClicked)
        self.ex.rightGridLayout.addWidget(ConnectBtn, 1, 0)

        FFTMagBtn = QPushButton("FFT Magnitud", self.ex.rightFrame)
        FFTMagBtn.resize (80,30)
        FFTMagBtn.clicked.connect(self.FFTMagBtnClicked)
        self.ex.rightGridLayout.addWidget(FFTMagBtn, 2, 0)

        ExitBtn = QPushButton("Salir", self.ex.rightFrame)
        ExitBtn.resize (80,30)
        ExitBtn.clicked.connect(qApp.quit)
        self.ex.rightGridLayout.addWidget(ExitBtn, 3, 0)

        send_command = QLabel('Comando: ')
        self.command_answer = QLabel(' ')
        self.send_Command_Edit = QLineEdit()

        self.ex.leftGridLayout.addWidget(send_command, 1, 0)
        self.ex.leftGridLayout.addWidget(self.send_Command_Edit, 1, 1)
        self.ex.leftGridLayout.addWidget(self.command_answer, 2, 1)

        self.setGeometry(300, 300, 800, 200)
        self.setWindowTitle('Command Test')
        self.show()


    def connectButtonClicked (self):
        s, self.instrumentList = SearchInstrument(self)
        if self.instrumentList:
            self.instrument = SelectInstrument(self.instrumentList)

        self.statusBar().showMessage(s)


    def FFTMagBtnClicked (self):
        if self.instrumentList:
            self.statusBar().showMessage("Comenzando la comunicacion")
            # rtn = FFT_Mag_Measure (self.instrument)
            # if rtn == -1:
                # self.command_answer.setText("No se pudo realizar la medición")

        else:
            self.statusBar().showMessage("Primero debe dar \"Conectar\"")
            rtn = FFT_Mag_Measure()





class HorizontalBox(QWidget):


    def __init__(self):
        super().__init__()
        self.initBox()


    def initBox(self):

        self.principalLayout = QHBoxLayout(self)
        #___________Left Frame___________
        self.leftFrame = QFrame(self)
        self.leftFrame.setFrameShape(QFrame.StyledPanel)
        self.leftFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.leftFrame)
        self.leftGridLayout = QGridLayout()
        self.verticalLayout.addLayout(self.leftGridLayout)
        self.principalLayout.addWidget(self.leftFrame)
        #___________Right Frame___________
        self.rightFrame = QFrame(self)
        self.rightFrame.setFrameShape(QFrame.StyledPanel)
        self.rightFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.rightFrame)
        self.rightGridLayout = QGridLayout()
        self.verticalLayout.addLayout(self.rightGridLayout)
        self.principalLayout.addWidget(self.rightFrame)




def SearchInstrument (self):
    self.instrumentList = []
    # Pedimos la lista de instrumentos
    rm=visa.ResourceManager('@py')
    #print(rm.list_resources('?*'))
    #print(rm.list_resources())

    if rm.list_resources():
        s = ("")
        for resource_obj in rm.list_resources():
	    # Abrimos un instrumento
            instrument_handler = rm.open_resource(resource_obj)
	    # Implementamos la clase instrumento base
            instrumento = Instrument(instrument_handler)
            self.instrumentList.append(instrumento)
	    # Imprimimos el ID el instrumento
            s = s + "\t" + instrumento.get_ID() + "\n"
        self.auxString = "Instrumentos conectados: " + s
        return self.auxString, self.instrumentList

    else:
        self.auxString = "No hay dispositivos para conectarse"
        return self.auxString, self.instrumentList


def SelectInstrument (instrumentList):
    return instrumentList[0]


#def FFT_Mag_Measure (instrument):
def FFT_Mag_Measure ():
    #FFTMag.core(instrument)
    rtn = FFTMag.AnalyzeFile()
    return 1




if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ConneTC_GUI()
    sys.exit(app.exec_())
