#!/usr/bin/env python2.7

#Author: Michael Doyle
#
#Purpose: First Attempt at XBee ZigBee Rx
#Note: Not adept in Python or any OOP for that matter
#		so go easy on me.

import serial
from xbee import ZigBee
import time, sys, datetime

serial_port = serial.Serial('/dev/serial0',9600)

zb = ZigBee(serial_port)

while True:
	try:
		data = zb.wait_read_frame()
		print data
	except KeyboardInterrupt:
		break
serial_port.close()
