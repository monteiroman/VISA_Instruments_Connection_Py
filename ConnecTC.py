#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, qApp, QWidget,
 QLabel, QLineEdit, QTextEdit, QGridLayout, QApplication, QPushButton,
 QHBoxLayout, QFrame, QVBoxLayout, QTabWidget)
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#from Agilent_U8903A import FFT_Magnitude
import Agilent_U8903A.FFT_Magnitude.core as FFTMag

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument



class ConnecTC_GUI(QMainWindow):


    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.title = 'Sistema de medición ConnecTC'
        self.left = 200
        self.top = 100
        self.width = 1000
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # for the subplot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.statusBar()

        self.show()



class MyTableWidget(QWidget):

    instrumentList = []


    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        Tabs(self)
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.connectTab = QWidget()
        self.FFTMagTab = QWidget()
        self.sendCommandTab = QWidget()
        self.tabs.resize(300,200)

        # Add tabs
        self.tabs.addTab(self.connectTab,"Conectar")
        self.tabs.addTab(self.FFTMagTab,"FFT Magnitud")
        self.tabs.addTab(self.sendCommandTab,"Probar comandos")

        # Create connectTab tab
        self.connectTab.layout = Tabs.connectTab(self, self.layout)
        self.connectTab.setLayout(self.connectTab.layout.principalLayout)

        # Create FFTMagTab tab
        self.FFTMagTab.layout = Tabs.FFTMagTab(self, self.layout)
        self.FFTMagTab.setLayout(self.FFTMagTab.layout.principalLayout)

        # Create sendCommandTab tab
        self.sendCommandTab.layout = Tabs.sendCommandTab(self, self.layout)
        self.sendCommandTab.setLayout(self.sendCommandTab.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


    def connectButtonClicked (self):
        s, self.instrumentList = SearchInstrument(self)
        if self.instrumentList:
            self.instrument = SelectInstrument(self.instrumentList)

        self.parent().statusBar().showMessage(s)


    def FFTMagBtnClicked (self):
        if self.instrumentList:
            self.parent().statusBar().showMessage("Comenzando la comunicacion")
            # rtn = FFT_Mag_Measure (self.instrument)
            # if rtn == -1:
                # self.command_answer.setText("No se pudo realizar la medición")

        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")
            x,y = FFT_Mag_Measure()
            ax = PlotSobplot(self.parent().figure)

            ax.plot(x,y)
            self.parent().canvas.draw()


    def sendButtonClicked (self):
        if self.instrumentList:
            self.command = self.send_Command_Edit.text()
            data = SendCommand (self.instrument, self.command)
            if data:
                self.command_answer.setText("Respuesta: " + data)

        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")



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
        self.principalLayout.addWidget(self.rightFrame)



class Tabs (MyTableWidget):


    def __init__(self, parent):
        super(MyTableWidget, self).__init__(parent)


    def FFTMagTab (self, layout):
        layout = HorizontalBox()

        self.FFTMagBtn = QPushButton("FFT Magnitud")
        self.FFTMagBtn.clicked.connect(self.FFTMagBtnClicked)
        layout.leftGridLayout.addWidget(self.FFTMagBtn, 1, 0)

        layout.verticalLayout.addWidget(self.parent().toolbar)
        layout.verticalLayout.addWidget(self.parent().canvas)

        return layout


    def connectTab (self, layout):
        layout = HorizontalBox()

        self.ConnectBtn = QPushButton("Conectar")
        self.ConnectBtn.clicked.connect(self.connectButtonClicked)
        layout.leftGridLayout.addWidget(self.ConnectBtn, 1, 0)

        self.ExitBtn = QPushButton("Salir")
        self.ExitBtn.clicked.connect(qApp.quit)
        layout.leftGridLayout.addWidget(self.ExitBtn, 2, 0)

        self.ImageLabel = QLabel(self)
        self.pixmap = QPixmap('sources/Pictures/logo1.png')
        self.ImageLabel.setPixmap(self.pixmap)
        layout.verticalLayout.addWidget(self.ImageLabel)

        return layout

    def sendCommandTab (self, layout):
        layout = QGridLayout()

        self.send_command = QLabel('Comando: ')
        layout.addWidget(self.send_command, 0, 0)

        self.SendBtn = QPushButton("Enviar Comando")
        self.SendBtn.clicked.connect(self.sendButtonClicked)
        layout.addWidget(self.SendBtn, 1, 0)

        self.send_Command_Edit = QLineEdit()
        layout.addWidget(self.send_Command_Edit, 0, 1)

        self.command_answer = QLabel(' ')
        layout.addWidget(self.command_answer, 1, 1)

        return layout




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



def FFT_Mag_Measure ():
    #FFTMag.core(instrument)
    x,y = FFTMag.AnalyzeFile()

    return x,y

def PlotSobplot (figure):
    ax = figure.add_subplot(111)
    ax.clear()
    ax.grid(True)
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Magnitude [dB]')
    ax.set_title("FFT Magnitud")

    return ax


def SendCommand (instrument, command):
    instrument.write(command)
    if command.find("?") != -1:
        data = instrument.read()
        #print("Datos recibidos: " + data)
        return data



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConnecTC_GUI()
    sys.exit(app.exec_())
