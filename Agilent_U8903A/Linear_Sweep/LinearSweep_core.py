#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:35:23 2018

@author: tiago
"""

import sys
import matplotlib.pyplot as plt
import numpy as np
import math as mat
import time

# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
sys.path.insert(0, 'Libreria')
# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument


def StartMeasure(instrument, startFreq=100, endFreq=1000, stepSize=200, outVolt=1, dwellTimeMS=1000):

    instrument.write("INIT:CONT:ANAL OFF, (@1)")    # Turns off the analyzer in channel 1
    instrument.write("INIT:CONT:ANAL OFF, (@2)")    # Turns off the analyzer in channel 2
    # instrument.write("INP:TYPE UNB, (@1)")          # sets the input of channel 1 to unbalanced
    # instrument.write("INP:TYPE UNB, (@2)")          # sets the input of channel 2 to unbalanced

    instrument.write("OUTP:STAT OFF, (@1)")         # Turns off the output of channel 1
    instrument.write("OUTP:STAT OFF, (@2)")         # Turns off the output of channel 2
    # instrument.write("OUTP:TYPE UNB, (@1)")         # sets the output of channel 1 to unbalanced mode
    # instrument.write("OUTP:TYPE UNB, (@2)")         # sets the output of channel 2 to unbalanced mode
    # instrument.write("OUTP:IMP IMP50, (@1)")        # sets the output of channel 1 to 50ohms
    # instrument.write("OUTP:IMP IMP50, (@2)")        # sets the output of channel 2 to 50ohms

    instrument.write("SOUR:SWE:INT ANAL")           # Sets the sweep generator interface to analog.
    instrument.write("SOUR:FUNC SINE, (@1)")        # Sets the generator waveform type to sine on channel 1.
    amplitudeSet = "SOUR:VOLT " + str(outVolt) + "Vp, (@1)"
    instrument.write(amplitudeSet)                  # Sets the amplitude of the sine waveform to 5 Vp.
    instrument.write("SOUR:SWE:REF:CHAN 1")         # Sets the sweep reference channel of the generator to channel 1.
    instrument.write("SOUR:SWE:CHAN 1")             # Sets channel 1 to perform sweep.
    instrument.write("SOUR:SWE:MODE ASW")           # Sets the sweep mode to Auto.
    instrument.write("SOUR:SWE:PAR FREQ")           # Sets the sweep parameter to frequency.
    instrument.write("SOUR:SWE:SPAC LIN, (@1)")     # Sets the spacing type to linear.
    dwellTime = "SOUR:SWE:DWEL1 " + str(dwellTimeMS)
    instrument.write(dwellTime)                     # Sets the dwell time to dwellTimeMS.
    instrument.write("SENS:MTIM GTR")               # Sets the measurement time to Gen Track.
    sweepStart = "SOUR:SWE:STAR " + str(startFreq)
    instrument.write(sweepStart)                    # Sets the sweep start value to startFreq.
    sweepEnd = "SOUR:SWE:STOP " + str(endFreq)
    instrument.write(sweepEnd)                      # Sets the sweep stop value to endFreq.
    sweepStep = "SOUR:SWE:STEP " + str(stepSize)
    instrument.write(sweepStep)                     # Sets the sweep step size to stepSize.
    instrument.write("SENS:SWE:INT ANAL")           # Sets the sweep analyzer interface to analog.
    instrument.write("SENS:SWE:REF:CHAN 1")         # Sets the sweep reference channel for measurement to channel 1.
    instrument.write("SENS:SWE:CHAN 1")             # Sets the analyzer channel to perform sweep to channel 2.
    instrument.write("SENS:FUNC1 FREQ, (@1)")       # Sets the measurement function 1 to frequency.
    instrument.write("SENS:FUNC2 VAC, (@1)")
    instrument.write("SENS:FUNC2:UNIT dBV, (@1)")        # Sets the measurement function 2 to dBV.
    instrument.write("INIT:SWE")                    # Initiates the sweep.
    aux = "1"
    while int(aux) is not 0:                        # Polls the status register to check if the measuring operation
        instrument.write("STAT:OPER:COND?")         # has completed. The condition register will return 0 if the
        time.sleep(6)
        aux = instrument.read()                     # operation has completed.
        print(aux)
        time.sleep(1)
    instrument.write("SOUR:SWE:VAL? (@1)")          # Acquires the X- axis sweep points values.
    xValues = instrument.read_raw()
    instrument.write("FETC:SWE? FUNC1, (@1)")       # Acquires the sweep result for function 1.
    freqValues = instrument.read_raw()
    instrument.write("FETC:SWE? FUNC2, (@1)")       # Acquires the sweep result for function 2
    vacValues = instrument.read_raw()

    xVal = xValues.split(str.encode(","))
    freqVal = freqValues.split(str.encode(","))
    vacVal = vacValues.split(str.encode(","))
    xVal = [float(i) for i in xVal]
    #print(xVal)
    freqVal = [float(i) for i in freqVal]
    #print(freqVal)
    vacVal = [float(i) for i in vacVal]

    #  for loop for print VacValues
    # n = 1
    # for i in vacVal:
    #     print(str(n) + " " + str(i))
    #     n = n + 1

    #print(vacVal)
    #print(f"type y: {type(vacVal)}")

    return xVal,freqVal,vacVal,1

def AnalyzeFile(startFreq=100, endFreq=1000, stepSize=200, outVolt=1, dwellTimeMS=1000):

    # Open file and read lines for debugging
    lines = [line.rstrip('\n') for line in open('RAW_Message2')]

    xValues = lines[0]
    freqValues = lines[1]
    vacValues = lines[2]

    xVal = xValues.split(",")
    freqVal = freqValues.split(",")
    vacVal = vacValues.split(",")
    xVal = [float(i) for i in xVal]
    #print(xVal)
    freqVal = [float(i) for i in freqVal]
    #print(freqVal)
    vacVal = [float(i) for i in vacVal]
    #print(vacVal)
    #print(f"type y: {type(vacVal)}")

    return xVal,freqVal,vacVal,1
