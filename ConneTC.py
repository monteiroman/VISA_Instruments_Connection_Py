#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp, QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout, QApplication, QPushButton, QHBoxLayout, QFrame, QVBoxLayout
from PyQt5.QtGui import QIcon

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument





class ConneTC_GUI(QMainWindow):


    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.ex = HorizontalBox()
        self.setCentralWidget(self.ex)

        self.statusBar()

        StartBtn = QPushButton("Empezar", self.ex.rightFrame)
        StartBtn.resize (80,30)
        StartBtn.clicked.connect(self.StartBtnClicked)
        self.ex.rightGridLayout.addWidget(StartBtn, 1, 0)

        TestBtn = QPushButton("Probar conexión", self.ex.rightFrame)
        TestBtn.resize (80,30)
        TestBtn.clicked.connect(self.testButtonClicked)
        self.ex.rightGridLayout.addWidget(TestBtn, 2, 0)

        ExitBtn = QPushButton("Salir", self.ex.rightFrame)
        ExitBtn.resize (80,30)
        ExitBtn.clicked.connect(qApp.quit)
        self.ex.rightGridLayout.addWidget(ExitBtn, 3, 0)

        f_start = QLabel('Fecuencia de inicio: ')
        f_end = QLabel('Fecuencia final: ')
        v_out = QLabel('Tension de salida: ')
        self.f_start_Edit = QLineEdit()
        self.f_end_Edit = QLineEdit()
        self.v_out_Edit = QLineEdit()

        self.ex.leftGridLayout.addWidget(f_start, 1, 0)
        self.ex.leftGridLayout.addWidget(f_end, 2, 0)
        self.ex.leftGridLayout.addWidget(v_out, 3, 0)
        self.ex.leftGridLayout.addWidget(self.f_start_Edit, 1, 1)
        self.ex.leftGridLayout.addWidget(self.f_end_Edit, 2, 1)
        self.ex.leftGridLayout.addWidget(self.v_out_Edit, 3, 1)

        self.setGeometry(300, 300, 500, 200)
        self.setWindowTitle('ConneTC')
        self.show()


    def testButtonClicked (self):
        s = SearchInstrument()
        self.statusBar().showMessage(s)


    def StartBtnClicked(self):
        print(self.f_start_Edit.text() + "\n" + self.f_end_Edit.text() + "\n" + self.v_out_Edit.text())



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




def SearchInstrument ():
    # Pedimos la lista de instrumentos
    rm=visa.ResourceManager('@py')
    #print(rm.list_resources('?*'))
    print(rm.list_resources())

    if rm.list_resources():
        s = ("")
        for resource_obj in rm.list_resources():
	    # Abrimos un instrumento
            instrument_handler = rm.open_resource(resource_obj)
	    # Implementamos la clase instrumento base
            instrumento = Instrument(instrument_handler)
	    # Imprimimos el ID el instrumento
            s = s + "\t" + instrumento.get_ID() + "\n"
        return "Instrumentos conectados: \n" + s
    else:
        return "No hay dispositivos conectados"




if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ConneTC_GUI()
    sys.exit(app.exec_())
