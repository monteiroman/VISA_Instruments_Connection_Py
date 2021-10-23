
## Introduction

Program to connect a linux pc with Agilent U8903A Audio Analyser via USB controlled by pyVisa.

The following functions are available:

* FFT Magnitude
* Linear Sweep


## Installation
Install these packages:

For USB communication:

    pip install pyusb

For implementation of the VISA standard directly in Python:

    pip install -U pyvisa-py

GUI is been managed with PyQt5:

    pip install pyqt5

And for output plots:

    pip install matplotlib

### USB permissions

Check at /etc/udev/rules.d if you have a file called 99-com.rules. If you do, write 
in a console:

    sudo cp  /etc/udev/rules.d/99-com.rules  /etc/udev/rules.d/99-com.rules.BAK

If you don't simply open 99-com.rules like this:

    sudo nano  /etc/udev/rules.d/99-com.rules

Add this line:

    SUBSYSTEM=="usb", MODE="0666", GROUP="usbusers"

And save the file.
Then add a group with name "usbusers"

    sudo groupadd usbusers

Add your user name to this group.

    sudo usermod -a -G usbusers USERNAME

reboot

### Test
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
