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
import Agilent_U8903A.FFT_Magnitude.FFTMagnitude_core as FFTMag
import Agilent_U8903A.Linear_Sweep.LinearSweep_core as LinearSweep

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, "Libreria")
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument

FFT_MAG = 0
LINEAR_SWEEP = 1


class ConnecTC_GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.title = "Sistema de medición ConnecTC"
        self.left = 200
        self.top = 100
        self.width = 1200
        self.height = 700
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.statusBar()

        self.show()

class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.instrument = 0
        self.instrumentList = []
        self.canvasHandlers = {}

        self.layout = QVBoxLayout(self)
        Tabs(self)
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.connectTab = QWidget()
        self.FFTMagTab = QWidget()
        self.linearSweepTab = QWidget()
        self.sendCommandTab = QWidget()
        self.tabs.resize(300,200)
        # Add tabs
        self.tabs.addTab(self.connectTab,"Conectar")
        self.tabs.addTab(self.FFTMagTab,"FFT Magnitud")
        self.tabs.addTab(self.linearSweepTab,"Sweep Lineal")
        self.tabs.addTab(self.sendCommandTab,"Probar comandos")
        # Create connectTab tab
        self.connectTab.layout = Tabs.connectTab_layout(self, self.layout)
        self.connectTab.setLayout(self.connectTab.layout.principalLayout)
        # Create FFTMagTab tab
        self.FFTMagTab.layout = Tabs.FFTMagTab_layout(self, self.layout)
        self.FFTMagTab.setLayout(self.FFTMagTab.layout.principalLayout)
        # Create linearSweep tab
        self.linearSweepTab.layout = Tabs.linearSweepTab_layout(self, self.layout)
        self.linearSweepTab.setLayout(self.linearSweepTab.layout.principalLayout)
        # Create sendCommandTab tab
        self.sendCommandTab.layout = Tabs.sendCommandTab_layout(self, self.layout)
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

    def FFTMagBtnClicked (self, points=256):
        if self.instrumentList:
            self.parent().statusBar().showMessage("Comenzando la comunicacion")
            x,y,status = FFT_Mag_Measure (self.instrument, points)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición")
                return
            ax = PlotSobplot(self.canvasHandlers["fftMag"], FFT_MAG)
            ax[0].plot(x,y)
            self.canvasHandlers["fftMag"].figure.canvas.draw()
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")
            x,y,status = FFT_Mag_Measure(self.instrument, points)
            ax = PlotSobplot(self.canvasHandlers["fftMag"], FFT_MAG)
            ax[0].plot(x,y)
            self.canvasHandlers["fftMag"].figure.canvas.draw()

    def sendButtonClicked (self):
        if self.instrumentList:
            self.command = self.send_Command_Edit.text()
            data = SendCommand (self.instrument, self.command)
            if data:
                self.command_answer.setText("Respuesta: " + data)
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")

    def sweepBtnClicked (self):
        if self.instrumentList:
            self.parent().statusBar().showMessage("Comenzando la comunicacion")
            self.startFreq = self.startFreq_Edit.text()
            self.endFreq = self.endFreq_Edit.text()
            self.stepSize = self.freqStep_Edit.text()
            self.outVolt = self.vac_Edit.text()
            self.dwellTimeMS = self.dwell_Edit.text()
            if not self.startFreq.isdigit() or not self.endFreq.isdigit() or not self.stepSize.isdigit() or not self.outVolt.isdigit() or not self.dwellTimeMS.isdigit():
                self.parent().statusBar().showMessage("Algun valor no es un número")
                return
            if int(self.startFreq) < 20 or int(self.startFreq) > 20000 or int(self.endFreq) < 20 or int(self.endFreq) > 20000 or int(self.startFreq) > int(self.endFreq):
                self.parent().statusBar().showMessage("La frecuencia de inicio debe ser menor a la final y ambas deben estar en un rango de 20 a 20000 Hz")
                return
            if int(self.stepSize) > int(self.endFreq):
                self.parent().statusBar().showMessage("El salto de frecuencia no puede ser mayor a la frecuencia final")
                return
            if int(self.outVolt) > 20:
                self.parent().statusBar().showMessage("La tension de salida tiene un rango de 1 a 20 volts")
                return
            x,y,status = Frequency_Sweep_Measure(self.instrument, self.startFreq, self.endFreq, self.stepSize, self.outVolt, self.dwellTimeMS)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición")
                return
            ax = PlotSobplot(self.canvasHandlers["linearSweep"], LINEAR_SWEEP)
            ax[0].plot(x,y)
            ax[1].plot(x,m)
            self.canvasHandlers["linearSweep"].figure.canvas.draw()
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")
            self.startFreq = self.startFreq_Edit.text()
            self.endFreq = self.endFreq_Edit.text()
            self.stepSize = self.freqStep_Edit.text()
            self.outVolt = self.vac_Edit.text()
            self.dwellTimeMS = self.dwell_Edit.text()
            if not self.startFreq.isdigit() or not self.endFreq.isdigit() or not self.stepSize.isdigit() or not self.outVolt.isdigit() or not self.dwellTimeMS.isdigit():
                self.parent().statusBar().showMessage("Algun valor no es un número")
                return
            if int(self.startFreq) < 20 or int(self.startFreq) > 20000 or int(self.endFreq) < 20 or int(self.endFreq) > 20000 or int(self.startFreq) > int(self.endFreq):
                self.parent().statusBar().showMessage("La frecuencia de inicio debe ser menor a la final y ambas deben estar en un rango de 20 a 20000 Hz")
                return
            if int(self.stepSize) > int(self.endFreq):
                self.parent().statusBar().showMessage("El salto de frecuencia no puede ser mayor a la frecuencia final")
                return
            if int(self.outVolt) > 20:
                self.parent().statusBar().showMessage("La tension de salida tiene un rango de 1 a 20 volts")
                return
            x,y,m,status = Frequency_Sweep_Measure(self.instrument, self.startFreq, self.endFreq, self.stepSize, self.outVolt, self.dwellTimeMS)
            ax = PlotSobplot(self.canvasHandlers["linearSweep"], LINEAR_SWEEP)
            ax[0].plot(x,y)
            ax[1].plot(x,m)
            self.canvasHandlers["linearSweep"].figure.canvas.draw()
        return

class Tabs (MyTableWidget):

    def __init__(self, parent):
        super(MyTableWidget, self).__init__(parent)

    def connectTab_layout (self, layout):
        layout = HorizontalBox()

        self.ConnectBtn = QPushButton("Conectar")
        self.ConnectBtn.clicked.connect(self.connectButtonClicked)
        layout.leftGridLayout.addWidget(self.ConnectBtn, 1, 0)

        self.ExitBtn = QPushButton("Salir")
        self.ExitBtn.clicked.connect(qApp.quit)
        layout.leftGridLayout.addWidget(self.ExitBtn, 2, 0)

        self.ImageLabel = QLabel(self)
        self.pixmap = QPixmap("sources/Pictures/logo1.png")
        self.ImageLabel.setPixmap(self.pixmap)
        layout.verticalLayout.addWidget(self.ImageLabel)

        return layout

    def FFTMagTab_layout (self, layout):
        layout = HorizontalBox()
        layout.leftFrame.setMinimumWidth(400)
        layout.leftFrame.setMaximumWidth(400)

        self.FFTMag256Btn = QPushButton("256 Puntos")
        self.FFTMag256Btn.clicked.connect(lambda: self.FFTMagBtnClicked(256))
        layout.leftGridLayout.addWidget(self.FFTMag256Btn, 1, 0)

        self.FFTMag512Btn = QPushButton("512 Puntos")
        self.FFTMag512Btn.clicked.connect(lambda: self.FFTMagBtnClicked(512))
        layout.leftGridLayout.addWidget(self.FFTMag512Btn, 2, 0)

        self.FFTMag1024Btn = QPushButton("1024 Puntos")
        self.FFTMag1024Btn.clicked.connect(lambda: self.FFTMagBtnClicked(1024))
        layout.leftGridLayout.addWidget(self.FFTMag1024Btn, 3, 0)

        canvas = FigureCanvas(plt.figure())
        toolbar = NavigationToolbar(canvas, self)
        layout.verticalLayout.addWidget(toolbar)
        layout.verticalLayout.addWidget(canvas)
        self.canvasHandlers["fftMag"] = canvas

        return layout

    def linearSweepTab_layout (self, layout):
        layout = HorizontalBox()
        layout.leftFrame.setMinimumWidth(400)
        layout.leftFrame.setMaximumWidth(400)

        self.sweepLabel = QLabel("Datos para el Sweep")
        self.sweepLabel.setMaximumWidth(200)
        layout.leftGridLayout.addWidget(self.sweepLabel, 1, 1)

        self.startFreqLabel = QLabel("Frecuencia de inicio: [Hz]")
        self.startFreqLabel.setMaximumWidth(250)
        layout.leftGridLayout.addWidget(self.startFreqLabel, 2, 1)

        self.startFreq_Edit = QLineEdit()
        self.startFreq_Edit.setText("100")
        self.startFreq_Edit.setMaximumWidth(80)
        layout.leftGridLayout.addWidget(self.startFreq_Edit, 2, 2)

        self.endFreqLabel = QLabel("Frecuencia final: [Hz]")
        self.endFreqLabel.setMaximumWidth(250)
        layout.leftGridLayout.addWidget(self.endFreqLabel, 3, 1)

        self.endFreq_Edit = QLineEdit()
        self.endFreq_Edit.setText("1000")
        self.endFreq_Edit.setMaximumWidth(80)
        layout.leftGridLayout.addWidget(self.endFreq_Edit, 3, 2)

        self.freqStepLabel = QLabel("Salto de frecuencia: [Hz]")
        self.freqStepLabel.setMaximumWidth(250)
        layout.leftGridLayout.addWidget(self.freqStepLabel, 4, 1)

        self.freqStep_Edit = QLineEdit()
        self.freqStep_Edit.setText("100")
        self.freqStep_Edit.setMaximumWidth(80)
        layout.leftGridLayout.addWidget(self.freqStep_Edit, 4, 2)

        self.vacLabel = QLabel("Tension de la señal de excitación: [V]")
        self.vacLabel.setMaximumWidth(250)
        layout.leftGridLayout.addWidget(self.vacLabel, 5, 1)

        self.vac_Edit = QLineEdit()
        self.vac_Edit.setText("2")
        self.vac_Edit.setMaximumWidth(80)
        layout.leftGridLayout.addWidget(self.vac_Edit, 5, 2)

        self.dwellLabel = QLabel("Permanencia de la señal: [mSeg]")
        self.dwellLabel.setMaximumWidth(250)
        layout.leftGridLayout.addWidget(self.dwellLabel, 6, 1)

        self.dwell_Edit = QLineEdit()
        self.dwell_Edit.setText("1000")
        self.dwell_Edit.setMaximumWidth(80)
        layout.leftGridLayout.addWidget(self.dwell_Edit, 6, 2)

        self.initSweep = QPushButton("Iniciar Sweep")
        self.initSweep.clicked.connect(lambda: self.sweepBtnClicked())
        layout.leftGridLayout.addWidget(self.initSweep, 7, 1, 4, 2)

        canvas = FigureCanvas(plt.figure())
        toolbar = NavigationToolbar(canvas, self)
        layout.verticalLayout.addWidget(canvas)
        layout.verticalLayout.addWidget(toolbar)
        self.canvasHandlers["linearSweep"] = canvas

        return layout

    def sendCommandTab_layout (self, layout):
        layout = QGridLayout()

        self.send_command = QLabel("Comando: ")
        layout.addWidget(self.send_command, 0, 0)

        self.SendBtn = QPushButton("Enviar Comando")
        self.SendBtn.clicked.connect(self.sendButtonClicked)
        layout.addWidget(self.SendBtn, 1, 0)

        self.send_Command_Edit = QLineEdit()
        layout.addWidget(self.send_Command_Edit, 0, 1)

        self.command_answer = QLabel(" ")
        layout.addWidget(self.command_answer, 1, 1)

        return layout

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

def SearchInstrument (self):
    self.instrumentList = []
    # Pedimos la lista de instrumentos
    rm=visa.ResourceManager("@py")
    #print(rm.list_resources("?*"))
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

def FFT_Mag_Measure (instrument, points=256):
    # x,y,status = FFTMag.StartMeasure(instrument, points)
    x,y,status = FFTMag.AnalyzeFile(points)
    return x,y,status

def Frequency_Sweep_Measure (instrument, startFreq=100, endFreq=1000, stepSize=200, outVolt=1, dwellTimeMS=1000):
    # x,y,status = LinearSweep.StartMeasure(instrument, startFreq, endFreq, stepSize, outVolt, dwellTimeMS)
    x,y,m,status = LinearSweep.AnalyzeFile(instrument, startFreq, endFreq, stepSize, outVolt, dwellTimeMS)
    return x,y,m,status

def PlotSobplot (figure, graphType):
    ax = []
    if graphType == FFT_MAG:
        ax.append(figure.figure.add_subplot(111))
        ax[0].clear()
        ax[0].grid(True)
        ax[0].set_xlabel("Frecuencia [Hz]")
        ax[0].set_ylabel("Magnitud [dB]")
        ax[0].set_title("FFT Magnitud")
    if graphType == LINEAR_SWEEP:
        ax.append(figure.figure.add_subplot(211))
        ax[0].clear()
        ax[0].grid(True)
        # ax[0].set_xscale("log")
        # ax[0].set_xlabel("Frecuencia [Hz]")
        ax[0].set_ylabel("Magnitud [dB]")
        ax[0].set_title("Barrido en fecuencia")
        ax.append(figure.figure.add_subplot(212))
        ax[1].clear()
        ax[1].grid(True)
        ax[1].set_xscale("log")
        ax[1].set_xlabel("Frecuencia [Hz]")
        ax[1].set_ylabel("Magnitud [dB]")
    return ax

def SendCommand (instrument, command):
    instrument.write(command)
    if command.find("?") != -1:
        data = instrument.read()
        #print("Datos recibidos: " + data)
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ConnecTC_GUI()
    sys.exit(app.exec_())
