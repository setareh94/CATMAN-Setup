#!/usr/bin/env python
import time
import serial
from xbee import XBee

ser = serial.Serial( 
        port='/dev/ttyAMA0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)
xbeeDevicesMacAddress = {'CATMAN2':'0013A200415A8686','CATMAN1':'0013A2004104746F'}

ser.isOpen()

print('Enter commands below\r\nInsert "exit" to exit')

jnput=1
while 1 :
    #get keyboard input
    jnput = input(">> ")
    if jnput == 'exit':
        ser.close()
        exit()
    else:
        ser.write(jnput.encode('ascii'))
        out = ''
        time.sleep
        while ser.inWaiting() > 0:
            out += ser.read(1)

        if out != '':
            print(">>" + out)
def __init__(self,*args,**kwargs):
    super(DigiMesh, self).__init__(*args,**kwargs)
    print("Initizing %s",DigiMesh)

def connection():
    #open the port
    ser = serial.Serial(port, baudrate, byteSize = 8, parity = 'N', stopbits = 1, timeout = None, xonxoff =1, dsrdtr = 1)

    #Create our API object

    xbee = ZigBee (ser, escape = True)
    DEST_ADDR_Serial = None
    h = ["","","NA","NA"]

    MessageTable= {}


    for i in DEST_ADDR_LONG:
        if (Success):
            MessageTable[i] = True
    #for key, value in xbeeDevicesMacAddress.iteritems:
        

        

    
