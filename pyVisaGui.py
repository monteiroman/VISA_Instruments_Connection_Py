#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 15:26:52 2018

Connection test with instruments by USB via PyVisa

@author: tiago
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
#import sys
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument



class PyVisaGui(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        btnSearch = QPushButton("Buscar dispositivos", self)
        btnSearch.resize (150,30)
        btnSearch.move(30, 50)
        btnSearch.clicked.connect(self.buttonClicked)

        btnExit = QPushButton("Salir", self)
        btnExit.move(170, 50)
        btnExit.clicked.connect(self.close)

        self.statusBar()

        self.setGeometry(300, 300, 400, 150)
        self.setWindowTitle('Connection Test')
        self.show()


    def buttonClicked(self):

        s = SearchInstrument()
        self.statusBar().showMessage(s)



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
    ex = PyVisaGui()
    sys.exit(app.exec_())
