#!/usr/bin/env python

import threading
import time

import XBee_API
import read_comm


x_bee = XBee_API.XBee_module(port='/dev/serial0',AP=2)
# NOTE: same thing could have been achieved by using: x_bee = XBee_API.XBee_module()
# NOTE: more options can be set when creating the object, like:
# - XBee Type: CE=[0: Router; 2: EndPoint]
# - Network ID: ID=hex number from 0x0000 to 0xffff [default 0x7fff]

x_bee.networkDiscover()
data = "Saying Hello"
x_bee.broadcastData(data);
# thread for the incoming XBee messages
comm_thread = threading.Thread(target=read_comm.read_comm, args=(x_bee,))
comm_thread.setDaemon(True)
comm_thread.start()

# keep the program alive till stopped by user
while 1:
    time.sleep(1.)
