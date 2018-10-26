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
import matplotlib.pyplot as plt
import numpy as np
import math as mat

import time

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

        StartBtn = QPushButton("Comenzar", self.ex.rightFrame)
        StartBtn.resize (80,30)
        StartBtn.clicked.connect(self.startButtonClicked)
        self.ex.rightGridLayout.addWidget(StartBtn, 2, 0)

        ExitBtn = QPushButton("Salir", self.ex.rightFrame)
        ExitBtn.resize (80,30)
        ExitBtn.clicked.connect(qApp.quit)
        self.ex.rightGridLayout.addWidget(ExitBtn, 3, 0)

        self.command_answer = QLabel('FFT Magnitude')
        self.ex.leftGridLayout.addWidget(self.command_answer, 2, 1)

        self.setGeometry(300, 300, 800, 200)
        self.setWindowTitle('Command Test')
        self.show()


    def connectButtonClicked (self):
        s, self.instrumentList = SearchInstrument(self)
        if self.instrumentList:
            self.instrument = SelectInstrument(self.instrumentList)

        self.statusBar().showMessage(s)


    def startButtonClicked (self):
        if self.instrumentList:
            StartMeasure(self.instrument)
        else:
            self.statusBar().showMessage("Primero debe dar \"Conectar\"")





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


def StartMeasure(instrument):
    instrument.write("DISP:ANAL:MODE MAGN")
    instrument.write("SENS:WAV:POIN 256")
    instrument.write("TRIG:GRAP:SOUR IMM")
    instrument.write("INIT:GRAP (@1)")
    aux = "1"
    while int(aux) is not 0:
        instrument.write("STAT:OPER:COND?")
        aux = instrument.read()
        print(aux)
        time.sleep(1)

    instrument.write("FETC:ARR? (@1) ")
    message = instrument.read_raw()

    #print(f"type #: {type(message[0])}")
    if message[0] != 35:
        return

    # file = open("RAW_Message", "wb")
    # file.write(message)
    # file.close()

    digits = message[1:2][0]-48
    print(f"type digits: {type(digits)} = {digits}")

    count = message[2:2+digits]
    print(f"type count: {type(count)} = {count}")


def AnalyzeFile():

    import struct

    file = open("RAW_Message", "rb")
    message = file.read()
    file.close()

    # convert ascii to int. First number of the file
    digits = message[1:2][0] - 48
    #print(f"type digits: {type(digits)} = {digits}")

    # extract the number of bytecount
    count = message[2:2+digits]
    #print(f"type count: {type(count)} = {count}")
    # convert bytes to string
    bytecount = count.decode("utf-8")
    #print(f"type count: {type(aux)} = {aux}")

    # string2int
    bytecount = int(bytecount)
    #print(f"type count: {type(aux)} = {aux}")

    # file info data chop
    bytesData = message[2+digits:-1]

    # converts file bytes in floats
    y = []
    for i in range(0, len(bytesData), 4):
        packed = bytesData[i:i+4]
        unpacked = struct.unpack("f", packed)
        y.append(unpacked[0])


    x = np.empty(256)
    filler = np.arange(0,256,1)
    index = np.arange(x.size)
    np.put(x,index,filler)
    

    plt.plot(x, y)
    plt.grid(True)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Magnitude [dB]')
    plt.title('FFT')
    plt.show()


if __name__ == '__main__':

    AnalyzeFile()

    # app = QApplication(sys.argv)
    # ex = ConneTC_GUI()
    # sys.exit(app.exec_())
