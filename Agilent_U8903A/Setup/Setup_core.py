#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

import sys
# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument

def Setup_Ports (instrument, type_G1, impedance_G1, type_G2, impedance_G2, type_A1, type_A2):
    instrument.write("INIT:CONT:ANAL OFF, (@1)")                                # Turns off the analyzer in channel 1
    instrument.write("INIT:CONT:ANAL OFF, (@2)")                                # Turns off the analyzer in channel 2
    instrument.write("OUTP:STAT OFF, (@1)")                                     # Turns off the output of channel 1
    instrument.write("OUTP:STAT OFF, (@2)")                                     # Turns off the output of channel 2

    type_G1_string = "OUTP:TYPE " + type_G1 + ", (@1)"
    instrument.write(type_G1_string)                                            # sets channel 1 output mode
    impedance_G1_string = "OUTP:IMP " + impedance_G1 + ", (@1)"
    instrument.write(impedance_G1_string)                                       # sets channel 1 output impedance

    type_G2_string = "OUTP:TYPE " + type_G2 + ", (@2)"
    instrument.write(type_G2_string)                                            # sets channel 2 output mode
    impedance_G2_string = "OUTP:IMP " + impedance_G2 + ", (@2)"
    instrument.write(impedance_G2_string)                                       # sets channel 2 output impedance

    type_A1_string = "INP:TYPE " + type_A1 + ", (@1)"
    instrument.write(type_A1_string)                                            # sets channel 1 input mode

    type_A2_string = "INP:TYPE " + type_A2 + ", (@2)"
    instrument.write(type_A2_string)                                            # sets channel 2 input mode
    return

def Setup_Debug (type_G1, impedance_G1, type_G2, impedance_G2, type_A1, type_A2):
    print("INIT:CONT:ANAL OFF, (@1)")
    print("INIT:CONT:ANAL OFF, (@2)")
    print("OUTP:STAT OFF, (@1)")
    print("OUTP:STAT OFF, (@2)")

    type_G1_string = "OUTP:TYPE " + type_G1 + ", (@1)"
    print(type_G1_string)
    impedance_G1_string = "OUTP:IMP " + impedance_G1 + ", (@1)"
    print(impedance_G1_string)

    type_G2_string = "OUTP:TYPE " + type_G2 + ", (@2)"
    print(type_G2_string)
    impedance_G2_string = "OUTP:IMP " + impedance_G2 + ", (@2)"
    print(impedance_G2_string)

    type_A1_string = "INP:TYPE " + type_A1 + ", (@1)"
    print(type_A1_string)

    type_A2_string = "INP:TYPE " + type_A2 + ", (@2)"
    print(type_A2_string)
    return
