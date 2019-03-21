
## Introduction

Program to connect a linux pc with Agilent U8903A Audio Analyser via USB controlled by pyVisa.

The following functions are available:

* FFT Magnitude
* Linear Sweep


## Installation

$ pip install pyusb

$ pip install -U pyvisa-py

## Test
PyVisa linux console test:

python -m visa info

Python PyVisa 

import visa

rm = visa.ResourceManager('@py')

print(rm.list_resources())

## Additional information 

U8903A Programmer's Reference.
http://www.swarthmore.edu/NatSci/echeeve1/Ref/U8903A/U8903-ProgramRef.pdf

User manual
https://literature.cdn.keysight.com/litweb/pdf/U8903-90002.pdf

