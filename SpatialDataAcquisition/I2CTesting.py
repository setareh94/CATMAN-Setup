#!/usr/bin/env python

import smbus2 as SMB
import os
import time

print("Now Establishing I2C Connection \n")

#First we can execute the bash command to detect I2C ports, 
#this shows us the matrix we are all used to.

os.system("i2cdetect -y 1")

bus = SMB.SMBus(1)

#we found out that the numbers are repeating on a period of 0to127 bytes.
#so thats a total of 128 bytes of data... but we have no idea wtf this is.
for number in range(0,63,1):
	GyroByte = bus.read_byte_data(0x6b,number)
	MagAccByte = bus.read_byte_data(0x1d,number)
	print("GyroByte: {}, MagAccelByte: {}, at register: {} ".format(GyroByte,MagAccByte,number))
