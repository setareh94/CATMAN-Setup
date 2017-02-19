import time
import serial
import io
from xbee import XBee
# setup port BT:ttyAMA0 or XB:ttyUSB0
ser = serial.Serial( 
        port='/dev/serial0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
		timeout=1    #time effecting readline buffer
)
# for readline() to function as of py2.7
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

ser.isOpen()

print('Awaiting incoming message:')

# read & print block
while 1:
    line = sio.readline()
    if line != '': 
        print(line)

ser.close()

"create a function to "
def main:
    try:
        xbee.send(frame='A',command='MY') #possibly required correct frame or modification within the device itself
        while(xbee.wait_read_frame()):
            print("") 
        
