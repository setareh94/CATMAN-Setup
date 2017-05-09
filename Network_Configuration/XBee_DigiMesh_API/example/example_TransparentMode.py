#!/usr/bin/env python

import threading
import time

import XBee_API
import read_comm


# authorship info
__author__      = "Francesco Vallegra"
__copyright__   = "Copyright 2017, MIT-SUTD"
__license__     = "MIT"


# create XBee module object
# NOTE: no need to specify serial port (can be found automatically) BUT the baud rate of the serial MUST be 9600
x_bee = XBee_API.XBee_module(AP=0)
# NOTE: more options can be set when creating the object, like:
# - XBee Type: CE=[0: Router; 2: EndPoint]
# - Network ID: ID=hex number from 0x0000 to 0xffff [default 0x7fff]

# thread for the incoming XBee messages
comm_thread = threading.Thread(target=read_comm.read_comm, args=(x_bee,))
comm_thread.setDaemon(True)
comm_thread.start()

# keep the program alive till stopped by user
while 1:
    time.sleep(1.)
