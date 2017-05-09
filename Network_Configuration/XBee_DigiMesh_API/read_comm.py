#!/usr/bin/env python

import sys
import threading
import time
import select       # for event-control the serial communication with the XBee  # NOTE: NOT WORKING ON WINDOWS!!

import XBee_API


# authorship info
__author__      = "Francesco Vallegra"
__copyright__   = "Copyright 2017, MIT-SUTD"
__license__     = "MIT"


##############################################################
# ITERATE ON EACH RECEIVED MESSAGE BY TYPE
def api_message_type(x_bee, XBmsg):
    """
    Differentiate by XBee message type

    :param x_bee: object of XBee_module class
    :param XBmsg: XBee_msg object taken from the buffer
    :return: None or text for testing purposes
    """
    # if frame_type is of received RF transmit
    if XBmsg.frame_type == 0x90:

        # identify sender
        sender = XBmsg.destAddrLow

        print("{}: {}".format(sender, XBmsg.data))

    # RSSI value reply
    elif XBmsg.frame_type == 0x88 and XBmsg.ATcmd == 'DB':
        data = XBmsg.data

        # get RSSI value
        RSSI = float(-data[-1])

        print("XBee last RSSI: " + str(RSSI))

    # Network Discovery reply
    elif XBmsg.frame_type == 0x88 and XBmsg.ATcmd == 'ND':
        data = XBmsg.data

        # identify node:
        sender = ''.join('{:02x}'.format(byte) for byte in data[6:10])

        # if XBmsg.paa
        RSSI = float(-data[-1])
        logStr = "XBee Network Discovery: {0} - RSSI: {1} dBm".format(sender, str(RSSI))
        print(logStr)
        return logStr

    # Find Neighbors reply
    elif (XBmsg.frame_type == 0x88 or XBmsg.frame_type == 0x97) and XBmsg.ATcmd == 'FN':
        data = XBmsg.data

        # identify node:
        sender = ''.join('{:02x}'.format(byte) for byte in data[6:10])

        # if XBmsg.paa
        RSSI = float(-data[-1])
        logStr = "XBee Find Neighbors: {0} - RSSI: {1} dBm".format(sender, str(RSSI))
        print(logStr)
        return logStr

    # received Route Information frame
    elif XBmsg.frame_type == 0x8D:

        # hop's sender
        senderH = XBmsg.responderAddr[:8]
        senderL = XBmsg.responderAddr[8:]

        # hop's receiver
        receiverH = XBmsg.receiverAddr[:8]
        receiverL = XBmsg.receiverAddr[8:]

        # test link quality
        x_bee.networkLinkTest(senderH, senderL, receiverH, receiverL)

    # received explicit RX -> network link test
    elif XBmsg.frame_type == 0x91:

        # sender
        sender = XBmsg.destAddrLow.lower()
        # receiver
        dest = ''.join('{:02x}'.format(byte) for byte in XBmsg.data[4:8])

        # paylod size
        paySize = int(''.join('{:02x}'.format(byte) for byte in XBmsg.data[8:10]), 16)
        # iterations
        iterations = int(''.join('{:02x}'.format(byte) for byte in XBmsg.data[10:12]), 16)

        # result
        if XBmsg.data[16] == 0x00:
            res = 'SUCCESS'
        else:
            res = 'ERROR'

        # average RSSI (signal strength)
        avgRSSI = float(-XBmsg.data[-1])

        logStr = "XBee Link Test: {0} - {1}: RSSI: {2} dBm (average on {3} iterations - {4} bytes each) [{5}]".format(
            sender, dest, avgRSSI, iterations, paySize, res)
        print(logStr)
        return logStr


def read_comm(x_bee_obj):
    """
    # buoy read comm with interrupt if on unix system

    :param x_bee_obj: object of XBee_module class
    :return:
    """
    print("Starting read_comm thread")
    if not sys.platform.startswith('win'):
        x_bee_obj.serial_port.nonblocking()  # needed when using "select"

    while 1:
        try:
            if sys.platform.startswith('win'):
                # select does not work on windows, so just sleep instead (more cpu usage)
                time.sleep(.1)
            else:
                # put a select on the serial with a maximum waiting of 10 sec
                select.select([x_bee_obj.serial_port], [], [], 10)

            # check for incoming messages reading from serial
            xbee_msg_list = x_bee_obj.readSerial()

        except:
            # could not read serial, then.. just try again
            xbee_msg_list = []

        if x_bee_obj.params['AP'] == '01' or x_bee_obj.params['AP'] == '02':
            # API mode without escape chars (AP=0x01) or with escape chars (AP=0x02)
            while xbee_msg_list:
                # get first element in the list
                try:
                    logStr = api_message_type(x_bee_obj, xbee_msg_list.pop(0))
                    if logStr:
                        x_bee_obj.logRAWtofile(logStr)
                except:
                    print("ERR: major error while decoding the message")
        elif x_bee_obj.params['AP'] == '00':
            # transparent mode
            if xbee_msg_list:
                print(xbee_msg_list.decode())
        else:
            # cannot be anything else.. notify user and ask to reboot
            print("ERR: wrong initialisation of the xbee.. please relaunch the program\n\r")


if __name__ == '__main__':
    # create XBee module object
    # x_bee = XBee_API.XBee_module()
    x_bee = XBee_API.XBee_module(baud=57600, AP=0, CE=2)

    # thread for the incoming XBee messages
    comm_thread = threading.Thread(target=read_comm, args=(x_bee,))
    comm_thread.setDaemon(True)
    comm_thread.start()

    # keep the program alive till stopped by user
    while 1:
        time.sleep(1.)
