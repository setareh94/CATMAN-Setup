#!/usr/bin/env python
import sys
import glob
import serial.tools.list_ports
from re import search


# authorship info
__author__      = "Brandon Zoss, Francesco Vallegra"
__copyright__   = "Copyright 2017, MIT-SUTD"
__license__     = "MIT"


def serial_ports():
    """
    Lists serial port names and checks if any is connected to a serial number of a usb to XBEE device

    :raises EnvironmentError: On unsupported or unknown platforms
    :returns: the port of the found XBee or None if none found
    """
    # depending on the system, reads available ports
    if sys.platform.startswith('win'):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "USB Serial Port" in str(p):
                print(p.description)
                return p.device
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):      # mac
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    # scan each found port and check the serial number
    XB = None
    for ser in ports:
        # look for serial devices, which name includes either a D or a A following a hyphen (-)
        # more at https://docs.python.org/2/library/re.html
        if bool(search('(?<=-)[DA]\w+', ser)) or 'USB0' in ser:
            XB = ser
            break

    # if not XB: raise EnvironmentError('No Digi-Mesh Radio Found')
    print("No Digi-Mesh Radio Found")
    
    return XB


if __name__ == '__main__':
    print(serial_ports())

