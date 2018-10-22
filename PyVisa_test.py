#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 16:38:23 2018

@author: tiago
"""

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument




# Pedimos la lista de instrumentos
rm=visa.ResourceManager('@py')
#print(rm.list_resources('?*'))
print(rm.list_resources())

if rm.list_resources():
    s = ("")
    for resource_obj in rm.list_resources():
	# Abrimos un instrumento
        instrument_handler=rm.open_resource(resource_obj)

	# Implementamos la clase instrumento base
        instrumento = Instrument(instrument_handler)

	# Imprimimos el ID el instrumento
        s = s + instrumento.print_ID()
        
    print("Instrumentos conectados: "+s)
        
else:
    print ("No hay dispositivo conectado")
    
    
