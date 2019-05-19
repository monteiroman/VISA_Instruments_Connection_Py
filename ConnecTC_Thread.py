#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

# TODO Hablar con cesar de SENSe:REFerence:IMPedance pagina 220 del manual

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QAction, qApp, QWidget,
 QLabel, QLineEdit, QTextEdit, QGridLayout, QApplication, QPushButton,
 QHBoxLayout, QFrame, QVBoxLayout, QTabWidget, QCheckBox, QButtonGroup, QAbstractButton, QGroupBox)
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import time
import threading
import os

#from Agilent_U8903A import modules
import Agilent_U8903A.FFT_Magnitude.FFTMagnitude_core as FFTMag
import Agilent_U8903A.Linear_Sweep.LinearSweep_core as LinearSweep
import Agilent_U8903A.Setup.Setup_core as Setup

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, "Libreria")
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument

FFT_MAG = 0
LINEAR_SWEEP = 1
NO_INSTRUMENT = 0                                                               #FOR DEBUGGIN PURPOSES
WITH_INSTRUMENT = 1                                                             #FOR DEBUGGIN PURPOSES
LOWBW = 30000
HIGHBW = 100000
BALANCED = "BAL"
UNBALANCED = "UNB"
IMP50 = "IMP50"
IMP100 = "IMP100"
IMP600 = "IMP600"
ON = "ON"
OFF = "OFF"


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
        self.configurationTab = QWidget()
        self.tabs.resize(300,200)
        # Add tabs
        self.tabs.addTab(self.connectTab,"Conectar")
        self.tabs.addTab(self.configurationTab,"Configuraciones")
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
        # Create configuration tab
        self.configurationTab.layout = Tabs.configurationTab_layout(self, self.layout)
        self.configurationTab.setLayout(self.configurationTab.layout)
        # Create sendCommandTab tab
        self.sendCommandTab.layout = Tabs.sendCommandTab_layout(self, self.layout)
        self.sendCommandTab.setLayout(self.sendCommandTab.layout)
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        # FFTMag Banwidth
        self.bw = LOWBW
        # Generators setup parameters
        self.type_G1 = UNBALANCED
        self.impedance_G1 = IMP600
        self.type_G2 = UNBALANCED
        self.impedance_G2 = IMP600
        # Analyzer setup parameters
        self.type_A1 = UNBALANCED
        self.type_A2 = UNBALANCED

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(),
            currentQTableWidgetItem.column(),
            currentQTableWidgetItem.text())

    def connectButtonClicked (self):
        if not self.instrument:
            s, self.instrumentList = SearchInstrument(self)
            if self.instrumentList:
                self.instrument = SelectInstrument(self.instrumentList)
            self.parent().statusBar().showMessage(s)
        else:
            self.parent().statusBar().showMessage("Ya se encuentra conectado al equipo")

    def FFTMagBtnClicked (self, points, bw):
        if self.instrumentList:
            self.parent().statusBar().showMessage("Comenzando la comunicacion...")
            mode = WITH_INSTRUMENT                                                              #FOR DEBUGGIN PURPOSES
            x,y,status = FFT_Mag_Measure (self.instrument, points, mode, bw)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición")
                return
            ax = PlotSobplot(self.canvasHandlers["fftMag"], FFT_MAG)
            ax[0].plot(x,y)
            self.canvasHandlers["fftMag"].figure.canvas.draw()
            self.parent().statusBar().showMessage("Listo!!")
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")
            mode = NO_INSTRUMENT                                                                #FOR DEBUGGIN PURPOSES
            x,y,status = FFT_Mag_Measure(self.instrument, points, mode, bw)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición")
                return
            ax = PlotSobplot(self.canvasHandlers["fftMag"], FFT_MAG)
            ax[0].plot(x,y)
            self.canvasHandlers["fftMag"].figure.canvas.draw()

    def sendButtonClicked (self):
        if self.instrumentList:
            self.command = self.send_Command_Edit.text()
            data = SendCommand(self.instrument, self.command)
            if data:
                self.command_answer.setText("Respuesta: " + data)
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")

    def sweepBtnClicked (self):
        if self.instrumentList:
            self.parent().statusBar().showMessage("Comenzando la comunicacion...")
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
            time.sleep(2)
            self.parent().statusBar().showMessage("Midiendo, por favor espere.")
            mode = WITH_INSTRUMENT                                                                                      #FOR DEBUGGIN PURPOSES
            x,y,m,status = Frequency_Sweep_Measure(self.instrument,
            self.startFreq, self.endFreq, self.stepSize, self.outVolt,
            self.dwellTimeMS, mode)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición.")
                return
            ax = PlotSobplot(self.canvasHandlers["linearSweep"], LINEAR_SWEEP)
            ax[0].plot(x,m)
            # ax[1].plot(x,m)
            self.canvasHandlers["linearSweep"].figure.canvas.draw()
            self.parent().statusBar().showMessage("Listo!!")
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
                self.parent().statusBar().showMessage(
                "La frecuencia de inicio debe ser menor a la final y ambas deben estar en un rango de 20 a 20000 Hz")
                return
            if int(self.stepSize) > int(self.endFreq):
                self.parent().statusBar().showMessage("El salto de frecuencia no puede ser mayor a la frecuencia final")
                return
            if int(self.outVolt) > 20:
                self.parent().statusBar().showMessage("La tension de salida tiene un rango de 1 a 20 volts")
                return
            mode = NO_INSTRUMENT                                                                                        #FOR DEBUGGIN PURPOSES
            x,y,m,status = Frequency_Sweep_Measure(self.instrument,
            self.startFreq, self.endFreq, self.stepSize, self.outVolt,
            self.dwellTimeMS, mode)
            if status == -1:
                self.parent().statusBar().showMessage("No se pudo realizar la medición.")
                return
            ax = PlotSobplot(self.canvasHandlers["linearSweep"], LINEAR_SWEEP)
            ax[0].plot(x,m)
            # ax[1].plot(x,m)
            self.canvasHandlers["linearSweep"].figure.canvas.draw()
        return

    def setFFTBw (self, btn):
        # print (btn.text()+" is selected")
        if(btn.text()=="30 kHz"):
            self.bw = LOWBW
        else:
            self.bw = HIGHBW

    def setupParameters_G1 (self, btn):
        # print (btn.text() + " is selected")
        if btn.text() == "Desbalanceada":
            self.imp600_G1.setChecked(True)
            self.imp100_G1.setEnabled(False)
            self.imp50_G1.setEnabled(True)
            self.type_G1 = UNBALANCED
            self.impedance_G1 = IMP600
        if btn.text() == "Balanceada":
            self.imp600_G1.setChecked(True)
            self.imp100_G1.setEnabled(True)
            self.imp50_G1.setEnabled(False)
            self.type_G1 = BALANCED
            self.impedance_G1 = IMP600
        if btn.text() == "50 ohms":
            self.impedance_G1 = IMP50
        if btn.text() == "100 ohms":
            self.impedance_G1 = IMP100
        if btn.text() == "600 ohms":
            self.impedance_G1 = IMP600
        # print("Generador 1 Tipo :" + self.type_G1 + " Impedancia: " + self.impedance_G1)

    def setupParameters_G2 (self, btn):
        # print (btn.text() + " is selected")
        if btn.text() == "Desbalanceada":
            self.imp600_G2.setChecked(True)
            self.imp100_G2.setEnabled(False)
            self.imp50_G2.setEnabled(True)
            self.type_G2 = UNBALANCED
            self.impedance_G2 = IMP600
        if btn.text() == "Balanceada":
            self.imp600_G2.setChecked(True)
            self.imp100_G2.setEnabled(True)
            self.imp50_G2.setEnabled(False)
            self.type_G2 = BALANCED
            self.impedance_G2 = IMP600
        if btn.text() == "50 ohms":
            self.impedance_G2 = IMP50
        if btn.text() == "100 ohms":
            self.impedance_G2 = IMP100
        if btn.text() == "600 ohms":
            self.impedance_G2 = IMP600
        # print("Generador 2 Tipo :" + self.type_G2 + " Impedancia: " + self.impedance_G2)

    def setupParameters_A1 (self, btn):
        # print (btn.text() + " is selected")
        if btn.text() == "Desbalanceada":
            self.type_A1 = UNBALANCED
        if btn.text() == "Balanceada":
            self.type_A1 = BALANCED
        # print("Analizador 1 Tipo :" + self.type_A1)

    def setupParameters_A2 (self, btn):
        # print (btn.text() + " is selected")
        if btn.text() == "Desbalanceada":
            self.type_A2 = UNBALANCED
        if btn.text() == "Balanceada":
            self.type_A2 = BALANCED
        # print("Analizador 2 Tipo :" + self.type_A2)

    def setParametersButtonClicked (self):
        if self.instrumentList:
            Setup.Setup_Ports(self.instrument, self.type_G1, self.impedance_G1,
                                self.type_G2, self.impedance_G2, self.type_A1,
                                self.type_A2)
        else:
            self.parent().statusBar().showMessage("Primero debe dar \"Conectar\"")
            # Setup.Setup_Debug(self.type_G1, self.impedance_G1,
            #                     self.type_G2, self.impedance_G2, self.type_A1,
            #                     self.type_A2)
        # print("Generador 1 Tipo :" + self.type_G1 + " Impedancia: " + self.impedance_G1)
        # print("Generador 2 Tipo :" + self.type_G2 + " Impedancia: " + self.impedance_G2)
        # print("Analizador 1 Tipo :" + self.type_A1)
        # print("Analizador 2 Tipo :" + self.type_A2)

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

        self.bwLabel = QLabel("Cantidad de puntos:")
        self.bwLabel.setMaximumWidth(200)
        layout.leftGridLayout.addWidget(self.bwLabel, 1, 0)

        self.FFTMag256Btn = QPushButton("256 Puntos")
        self.FFTMag256Btn.clicked.connect(lambda: self.FFTMagBtnClicked(256, self.bw))
        layout.leftGridLayout.addWidget(self.FFTMag256Btn, 2, 1)

        self.FFTMag512Btn = QPushButton("512 Puntos")
        self.FFTMag512Btn.clicked.connect(lambda: self.FFTMagBtnClicked(512, self.bw))
        layout.leftGridLayout.addWidget(self.FFTMag512Btn, 3, 1)

        self.FFTMag1024Btn = QPushButton("1024 Puntos")
        self.FFTMag1024Btn.clicked.connect(lambda: self.FFTMagBtnClicked(1024, self.bw))
        layout.leftGridLayout.addWidget(self.FFTMag1024Btn, 4, 1)

        self.bwLabel = QLabel("Ancho de banda: ")
        self.bwLabel.setMaximumWidth(200)
        layout.leftGridLayout.addWidget(self.bwLabel, 5, 0)

        self.lowBw = QCheckBox("30 kHz")
        self.lowBw.setChecked(True)
        layout.leftGridLayout.addWidget(self.lowBw, 6,1)

        self.highBw = QCheckBox("100 kHz")
        layout.leftGridLayout.addWidget(self.highBw, 6,2)

        self.FFTButtonGroup = QButtonGroup()
        self.FFTButtonGroup.addButton(self.lowBw, 1)
        self.FFTButtonGroup.addButton(self.highBw, 2)

        self.FFTButtonGroup.buttonClicked[QAbstractButton].connect(self.setFFTBw)

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

    def configurationTab_layout (self, layout):
        layout = QGridLayout()
# ------Generator 1--------
        self.generator1GroupBox = QGroupBox("Generador 1:")

        self.typeTitle_G1 = QLabel("Tipo de salida:")
        self.BalOutput_G1 = QCheckBox("Balanceada")
        self.UnbalOutput_G1 = QCheckBox("Desbalanceada")
        self.UnbalOutput_G1.setChecked(True)

        self.typeButtonGroup_G1 = QButtonGroup()
        self.typeButtonGroup_G1.addButton(self.BalOutput_G1, 1)
        self.typeButtonGroup_G1.addButton(self.UnbalOutput_G1, 2)

        self.typeButtonGroup_G1.buttonClicked[QAbstractButton].connect(self.setupParameters_G1)

        self.type_hbox_G1 = QHBoxLayout()
        self.type_hbox_G1.addWidget(self.BalOutput_G1)
        self.type_hbox_G1.addWidget(self.UnbalOutput_G1)

        self.impTitle = QLabel("Impedancia de salida:")
        self.imp50_G1 = QCheckBox("50 ohms")
        self.imp100_G1 = QCheckBox("100 ohms")
        self.imp600_G1 = QCheckBox("600 ohms")
        self.imp600_G1.setChecked(True)
        self.imp100_G1.setEnabled(False)

        self.impButtonGroup_G1 = QButtonGroup()
        self.impButtonGroup_G1.addButton(self.imp50_G1, 1)
        self.impButtonGroup_G1.addButton(self.imp100_G1, 2)
        self.impButtonGroup_G1.addButton(self.imp600_G1, 3)

        self.impButtonGroup_G1.buttonClicked[QAbstractButton].connect(self.setupParameters_G1)

        self.imp_hbox_G1 = QHBoxLayout()
        self.imp_hbox_G1.addWidget(self.imp50_G1)
        self.imp_hbox_G1.addWidget(self.imp100_G1)
        self.imp_hbox_G1.addWidget(self.imp600_G1)

        self.generator_vBox_G1 = QVBoxLayout()
        self.generator_vBox_G1.addWidget(self.typeTitle_G1)
        self.generator_vBox_G1.addLayout(self.type_hbox_G1)
        self.generator_vBox_G1.addWidget(self.impTitle)
        self.generator_vBox_G1.addLayout(self.imp_hbox_G1)

        self.generator1GroupBox.setLayout(self.generator_vBox_G1)

        layout.addWidget(self.generator1GroupBox, 2, 0)
# ------Generator 1--------
# ------Generator 2--------
        self.generator2GroupBox = QGroupBox("Generador 2:")

        self.typeTitle_G2 = QLabel("Tipo de salida:")
        self.BalOutput_G2 = QCheckBox("Balanceada")
        self.UnbalOutput_G2 = QCheckBox("Desbalanceada")
        self.UnbalOutput_G2.setChecked(True)

        self.typeButtonGroup_G2 = QButtonGroup()
        self.typeButtonGroup_G2.addButton(self.BalOutput_G2, 1)
        self.typeButtonGroup_G2.addButton(self.UnbalOutput_G2, 2)

        self.typeButtonGroup_G2.buttonClicked[QAbstractButton].connect(self.setupParameters_G2)

        self.type_hbox_G2 = QHBoxLayout()
        self.type_hbox_G2.addWidget(self.BalOutput_G2)
        self.type_hbox_G2.addWidget(self.UnbalOutput_G2)

        self.impTitle = QLabel("Impedancia de salida:")
        self.imp50_G2 = QCheckBox("50 ohms")
        self.imp100_G2 = QCheckBox("100 ohms")
        self.imp600_G2 = QCheckBox("600 ohms")
        self.imp600_G2.setChecked(True)
        self.imp100_G2.setEnabled(False)

        self.impButtonGroup_G2 = QButtonGroup()
        self.impButtonGroup_G2.addButton(self.imp50_G2, 1)
        self.impButtonGroup_G2.addButton(self.imp100_G2, 2)
        self.impButtonGroup_G2.addButton(self.imp600_G2, 3)

        self.impButtonGroup_G2.buttonClicked[QAbstractButton].connect(self.setupParameters_G2)

        self.imp_hbox_G2 = QHBoxLayout()
        self.imp_hbox_G2.addWidget(self.imp50_G2)
        self.imp_hbox_G2.addWidget(self.imp100_G2)
        self.imp_hbox_G2.addWidget(self.imp600_G2)

        self.generator_vBox_G2 = QVBoxLayout()
        self.generator_vBox_G2.addWidget(self.typeTitle_G2)
        self.generator_vBox_G2.addLayout(self.type_hbox_G2)
        self.generator_vBox_G2.addWidget(self.impTitle)
        self.generator_vBox_G2.addLayout(self.imp_hbox_G2)

        self.generator2GroupBox.setLayout(self.generator_vBox_G2)

        layout.addWidget(self.generator2GroupBox, 3, 0)
# ------Generator 2--------
# ------Analyzer 1--------
        self.analyzer1GroupBox = QGroupBox("Analizador 1:")

        self.typeTitle_A1 = QLabel("Tipo de salida:")
        self.BalOutput_A1 = QCheckBox("Balanceada")
        self.UnbalOutput_A1 = QCheckBox("Desbalanceada")
        self.UnbalOutput_A1.setChecked(True)

        self.typeButtonGroup_A1 = QButtonGroup()
        self.typeButtonGroup_A1.addButton(self.BalOutput_A1, 1)
        self.typeButtonGroup_A1.addButton(self.UnbalOutput_A1, 2)

        self.typeButtonGroup_A1.buttonClicked[QAbstractButton].connect(self.setupParameters_A1)

        self.type_hbox_A1 = QHBoxLayout()
        self.type_hbox_A1.addWidget(self.BalOutput_A1)
        self.type_hbox_A1.addWidget(self.UnbalOutput_A1)

        self.analyzer_vBox_A1 = QVBoxLayout()
        self.analyzer_vBox_A1.addWidget(self.typeTitle_A1)
        self.analyzer_vBox_A1.addLayout(self.type_hbox_A1)

        self.analyzer1GroupBox.setLayout(self.analyzer_vBox_A1)

        layout.addWidget(self.analyzer1GroupBox, 2, 1)
# ------Analyzer 1--------
# ------Analyzer 2--------
        self.analyzer2GroupBox = QGroupBox("Analizador 1:")

        self.typeTitle_A2 = QLabel("Tipo de salida:")
        self.BalOutput_A2 = QCheckBox("Balanceada")
        self.UnbalOutput_A2 = QCheckBox("Desbalanceada")
        self.UnbalOutput_A2.setChecked(True)

        self.typeButtonGroup_A2 = QButtonGroup()
        self.typeButtonGroup_A2.addButton(self.BalOutput_A2, 1)
        self.typeButtonGroup_A2.addButton(self.UnbalOutput_A2, 2)

        self.typeButtonGroup_A2.buttonClicked[QAbstractButton].connect(self.setupParameters_A2)

        self.type_hbox_A2 = QHBoxLayout()
        self.type_hbox_A2.addWidget(self.BalOutput_A2)
        self.type_hbox_A2.addWidget(self.UnbalOutput_A2)

        self.analyzer_vBox_A2 = QVBoxLayout()
        self.analyzer_vBox_A2.addWidget(self.typeTitle_A2)
        self.analyzer_vBox_A2.addLayout(self.type_hbox_A2)

        self.analyzer2GroupBox.setLayout(self.analyzer_vBox_A2)

        layout.addWidget(self.analyzer2GroupBox, 3, 1)
# ------Analyzer 2--------

        self.confTitle = QLabel(self)
        self.confTitle.setText("Configuracion de los puertos frontales:")
        layout.addWidget(self.confTitle, 0, 0)

        self.generatorImageLabel = QLabel(self)
        self.generatorPixmap = QPixmap("sources/Pictures/generator.png")
        self.generatorImageLabel.setPixmap(self.generatorPixmap)
        layout.addWidget(self.generatorImageLabel, 1, 0)

        self.analyzerImageLabel = QLabel(self)
        self.analyzerPixmap = QPixmap("sources/Pictures/analyzer.png")
        self.analyzerImageLabel.setPixmap(self.analyzerPixmap)
        layout.addWidget(self.analyzerImageLabel, 1, 1)

        self.SetParameters = QPushButton("Aplicar cambios")
        self.SetParameters.clicked.connect(self.setParametersButtonClicked)
        layout.addWidget(self.SetParameters, 4, 0, 2, 2)

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

def FFT_Mag_Measure (instrument, points, mode=WITH_INSTRUMENT, bw=LOWBW):
    magFFT_Thread = FFT_Thread(name = "FFT_Thread")
    if mode==WITH_INSTRUMENT:                                                   #FOR DEBUGGIN PURPOSES
        magFFT_Thread.setFFTData(points, bw, instrument)
    else:                                                                       #FOR DEBUGGIN PURPOSES
        magFFT_Thread.setFFTData(points, bw)
    magFFT_Thread.start()
    magFFT_Thread.join()
    x,y,status = magFFT_Thread.getFFTData()
    return x,y,status

def Frequency_Sweep_Measure (instrument, startFreq=100, endFreq=1000,
                stepSize=200, outVolt=1, dwellTimeMS=1000, mode=WITH_INSTRUMENT):
    sweep_Thread = Sweep_Thread(name = "Sweep_Thread")
    if mode == WITH_INSTRUMENT:
        sweep_Thread.setSweepData(startFreq, endFreq, stepSize, outVolt, dwellTimeMS,
                            instrument)
    else:
        sweep_Thread.setSweepData(startFreq, endFreq, stepSize, outVolt, dwellTimeMS)
    sweep_Thread.start()
    sweep_Thread.join()
    x,y,m,status = sweep_Thread.getSweepData()
    saveSweepData(x,m)
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
        ax.append(figure.figure.add_subplot(111))
        # ax[0].clear()
        # ax[0].grid(True)
        # # ax[0].set_xscale("log")
        # # ax[0].set_xlabel("Frecuencia [Hz]")
        # ax[0].set_ylabel("Frecuencia [Hz]")
        # ax[0].set_title("Barrido en fecuencia")
        # ax.append(figure.figure.add_subplot(212))
        ax[0].clear()
        ax[0].grid(True)
        ax[0].set_xscale("log")
        ax[0].set_xlabel("Frecuencia [Hz]")
        ax[0].set_ylabel("Magnitud [dB]")
    return ax

def SendCommand (instrument, command):
    instrument.write(command)
    if command.find("?") != -1:
        data = instrument.read()
        #print("Datos recibidos: " + data)
        return data
    return

def saveSweepData(x, m):
    dirpath = os.getcwd()
    measureFile = open(dirpath + "/SweepData.csv", "w+")
    for i in range(len(x)):
        measureFile.write(str(x[i]) + "," + str(m[i]) + "\n")
    return

class FFT_Thread(threading.Thread):
    def setFFTData(self, points, bw, instrument=-1):
        self.instrument = instrument
        self.points = points
        self.bw = bw
    def getFFTData(self):
        return self.x, self.y, self.status

    def run(self):
        if self.instrument == -1:
            try:
                self.x, self.y, self.status = FFTMag.AnalyzeFile(self.points, self.bw)
            except:
                self.x = 0
                self.y = 0
                self.status = -1
        else:
            try:
                self.x, self.y, self.status = FFTMag.StartMeasure(self.instrument, self.points, self.bw)
            except:
                self.x = 0
                self.y = 0
                self.status = -1

class Sweep_Thread(threading.Thread):
    def setSweepData(self, startFreq, endFreq, stepSize, outVolt, dwellTimeMS,
                        instrument=-1):
        self.instrument = instrument
        self.startFreq = startFreq
        self.endFreq = endFreq
        self.stepSize = stepSize
        self.outVolt = outVolt
        self.dwellTimeMS = dwellTimeMS
    def getSweepData(self):
        return self.x, self.y, self.m, self.status

    def run(self):
        if self.instrument == -1:
            try:
                self.x, self.y, self.m, self.status = LinearSweep.AnalyzeFile(self.startFreq,
                self.endFreq, self.stepSize, self.outVolt, self.dwellTimeMS)
            except:
                self.x = 0
                self.y = 0
                self.m = 0
                self.status = -1
        else:
            try:
                self.x, self.y, self.m, self.status = LinearSweep.StartMeasure(self.instrument,
                self.startFreq, self.endFreq, self.stepSize, self.outVolt, self.dwellTimeMS)
            except:
                self.x = 0
                self.y = 0
                self.m = 0
                self.status = -1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ConnecTC_GUI()
    sys.exit(app.exec_())
