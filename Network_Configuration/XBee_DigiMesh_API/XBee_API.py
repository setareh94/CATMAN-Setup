#!/usr/bin/env python

from serial import Serial
import time
import sys
from datetime import datetime
import os

# import XBee_msg classes and method for finding a SBee serial device
from XB_Finder import serial_ports
from XBee_msg import *


# authorship info
__author__      = "Francesco Vallegra, Brandon Zoss"
__copyright__   = "Copyright 2015-2017, MIT-SUTD"
__license__     = "MIT"


# create dictionary for API operations
APIop = {0x88: ['AT Command Response', XB_locAT_IN, 1],     # name, reference to function, print (y/n)
         0x8B: ['Transmit Status', XB_RFstatus_IN, 0],
         0x8D: ['Route Information Packet', XB_RouteInfo_IN, 1],
         0x90: ['Receive Packet (AO=0)', XB_RF_IN, 0],
         0x91: ['Explicit Rx Indicator (AO=1)', XB_RFexpl_IN, 1],
         0x97: ['Remote Command Response', XB_remAT_IN, 1]}


# ===============================================================================
# ===============================================================================
#   XBeeAPI class
# ===============================================================================
# ===============================================================================
class XBee_module:

    def __init__(self, port=None, baud=9600, ID=0x7FFF, AP=0x02, CE=0x00, NO=0x04):
        """
        XBee initialization
        """
        # network ID
        self.ID = '%x' % ID
        # API mode enabled/disabled [0:no API; 1:API no escape seq; 2:API with escape seq]
        self.AP = '%x' % AP
        # Routing/Message mode [0: Router; 1:NA; 2:EndNode]
        self.CE = '%x' % CE
        # additional info
        self.NO = '%x' % NO

        # if no port provided, try to find it between the ones available, depending on the OS being used
        self.port = port
        if port is None:
            self.port = serial_ports()
        # baud rate to use.. may be not the one preset in the XBee
        self.baud = baud

        # list where to save received transmits (as objects of class XBee_msg or children)
        self.RxMsg = list()

        # input buffer including all bytes from serial
        self.RxBuff = bytearray()

        # XBee configuration
        self.XBconf = {'ID': self.ID,   # Network ID (between 0x0000 and 0x7FFF)
                       'AP': self.AP,   # API mode
                       'CE': self.CE,   # Routing/Message mode
                       'NO': self.NO,   # include additional info when network and neighbor discovery
                       'DL': 'FFFF',    # destination Address High to broadcast
                       'DH': '0'}       # destination Address Low to broadcast

        # enquire main parameters from local XBee (initial value is the number of bytes to use)
        self.params = {'ID': 4,        # Network ID (between 0x0000 and 0x7FFF)
                       'CE': 2,        # Node type
                       'BH': 2,        # Broadcast radius
                       'SH': 8,        # Local Address High (high 32bit RF module's address)
                       'SL': 8,        # Local Address Low (low 32bit RF module's address)
                       'DH': 8,        # Destination Address High
                       'DL': 8,        # Destination Address Low
                       'AP': 2}        # API mode [0:no API; 1:API no escape seq; 2:API with escape seq]

        # diagnostic parameters
        self.diagn = {'GD': [],         # number of good frames
                      'EA': [],         # number of timeouts
                      'TR': [],         # number of transmission errors
                      'DB': []}         # RSSI (signal strength) of last received packet [-dBm]

        # set serial port and baud
        self.serial_port = Serial(port=self.port, baudrate=self.baud)

        # make sure no information is in the serial buffer
        self._flush()
        time.sleep(0.2)
        self._flush()

        # start logging RAW data from/to XBee
        path = "./Output/"
        if not os.path.exists(path):
            os.makedirs(path)
        self.rawLogFileIDstr = path + "XBeeRAW_log" + str(datetime.datetime.now()) + ".txt"
        print("Storing RAW Xbee log to: " + self.rawLogFileIDstr)

        logStr = '\n\nXBee Communicating via ' + self.port
        print(logStr)
        self.logRAWtofile(logStr)
        xbee_type = 'ERR'
        if CE == 0:
            xbee_type = 'Router'
        elif CE == 2:
            xbee_type = 'EndPoint'
        xbee_mode = 'ERR'
        if AP == 0:
            xbee_mode = 'Transparent Mode'
        elif AP == 1:
            xbee_mode = 'API mode (without escaping chars)'
        elif AP == 2:
            xbee_mode = 'API mode (with escaping chars)'
        logStr = 'Programming XBee for\n\ttype: {}\n\t{}\n\tNetworkID: {}'.format(xbee_type,
                                                                                  xbee_mode,
                                                                                  self.XBconf['ID'])
        print(logStr)
        self.logRAWtofile(logStr)

        # set parameters' values from self.XBconf
        ATregs = list()
        ATvals = list()
        for reg in self.XBconf:
            ATregs.append(reg)
            ATvals.append(self.XBconf[reg])
        self.cmd_mode_set_registries(ATregs, ATvals, first_init=True)

        logStr = '\nReading Settings from XBee..'
        print(logStr)
        self.logRAWtofile(logStr)

        # get parameters' values from XBee memory
        for param in self.params:
            reg_value = self.cmd_mode_read_registry(param)

            if reg_value is not None:
                reg_value = '%s' % reg_value.decode()
                while len(reg_value) < self.params[param]:
                    reg_value = '0' + reg_value
                logStr = "\tRegistry '{}': '0x{}'".format(param, reg_value)
                print(logStr)
                self.logRAWtofile(logStr)

                # set params[AT] to the received value
                self.params[param] = reg_value
        print('')

        logStr = 'XBee initialization complete!\n'
        print(logStr)
        self.logRAWtofile(logStr)


# ===============================================================================
#   define methods for Command Mode operations
# ===============================================================================
    def cmd_mode_set_registries(self, registries, values, first_init=False):
        """
        Method used to manually set registries of the XBee in case we don't know what is the last configuration flashed.
        Note however that the BaudRate must be correct..

        :param registries: list of registries to set
        :param values: list of values for the registries
        :param first_init: flag to know if it's the first time we set registries or not. If yes, the guard time will
                be changed to 10ms instead of 1000ms so to make the process of manually settings registries faster
        :return:
        """
        preset_baud = self.baud

        # wait guard time
        if first_init:
            time.sleep(1.)  # default guard time
        else:
            time.sleep(.01)

        # start command mode
        self._write(bytearray("+++".encode()))

        # wait guard time
        if first_init:
            ok_received = False
            time_req = time.time()
            input_chars = bytearray([])
            while not ok_received:
                if time.time() - time_req > 1.2:
                    print("ERR: OK not received!")
                    break

                while self.serial_port.inWaiting():
                    input_chars.extend(self.serial_port.read())
                if len(input_chars) >= 3:
                    # note that other messages could have been received while starting the command mode, but nothing
                    # can be received after the command mode is set, which is confirmed by 'OK\r' reply from XBee
                    if input_chars[-3:] == bytearray([0x4F, 0x4B, 0x0D]):
                        ok_received = True

            # if still not received after 1.2 seconds, it means we are using a wrong baud rate
            if not ok_received:
                # the following function will automatically open the serial in the correct baud if any found
                preset_baud = self.check_serial_baud_rate()
        else:
            time.sleep(.01)

        if first_init and preset_baud != self.baud:
            # need to change the baud on the module and in the serial communication

            # define dictionary with correct values to set registry
            xbee_baud = {1200: '0',
                         2400: '1',
                         4800: '2',
                         9600: '3',
                         19200: '4',
                         38400: '5',
                         57600: '6',
                         115200: '7'}

            if self.baud not in xbee_baud:
                logStr = "'{}' not valid baud vaule! keeping preset value ('{}')".format(self.baud, preset_baud)
                print(logStr)
                self.logRAWtofile(logStr)
            else:
                logStr = "Programing the XBee for baud '{}'".format(self.baud)
                print(logStr)
                self.logRAWtofile(logStr)

                # send command by making sure to write first and apply later
                self._write(bytearray("ATBD{}\r,ATWR\r".format(xbee_baud[self.baud]).encode()))
                time.sleep(.06)
                self._write(bytearray("ATAC\r".encode()))

                # restart local serial connection with new baud
                self.serial_port.close()
                time.sleep(.2)
                self.serial_port = Serial(port=self.port, baudrate=self.baud)

        # flush buffer to make sure no message arrived while setting command mode
        self._flush()

        settings_list = ''
        # set guard time to 10ms instead of 1s
        if first_init:
            settings_list += ',ATGTA\r'
        for reg, val in zip(registries, values):
            settings_list += ',AT{}{}\r'.format(reg, val)

        # apply changes and write
        settings_list += ',ATAC\r,ATWR\r'

        # write
        self._write(bytearray(settings_list.encode()))

        # there should be no errors, so flush buffers   # TODO: check needed anyway??
        time.sleep(0.2)
        self._flush()

        # exit command mode (Send command after flushing to give time to the XBee to write commands ot flash memory)
        self._write(bytearray("ATCN\r".encode()))
        time.sleep(0.1)
        self._flush()

    def cmd_mode_read_registry(self, registry):
        """
        Method used to manually read a registry from the XBee using the command mode

        :param registry: registry name as per DigiMesh documentation
        :return: answer in hex from the XBee or None if no answer from XBee
        """
        # wait guard time
        time.sleep(.01)

        # start command mode
        self._write(bytearray("+++".encode()))

        # wait guard time
        time.sleep(.01)

        ok_received = False
        time_req = time.time()
        input_chars = bytearray([])
        while not ok_received:
            if time.time() - time_req > 1.:
                print("ERR: OK not received!")
                return None

            while self.serial_port.inWaiting():
                input_chars.extend(self.serial_port.read())
            if len(input_chars) >= 3:
                # here note that other messages could have been received while starting the command mode, but nothing
                # can be received after the command mode is set, which is confirmed by 'OK\r' reply from XBee
                if input_chars[-3:] == bytearray([0x4F, 0x4B, 0x0D]):
                    ok_received = True

        # send manual command to get the registry value and command to exit command mode
        self._write(bytearray('AT{}\r,ATCN\r'.format(registry).encode()))

        # read XBee reply
        time_req = time.time()
        input_chars = bytearray([])
        while time.time() - time_req < 1.:
            while self.serial_port.inWaiting():
                input_chars.extend(self.serial_port.read())

            if len(input_chars) >= 3:
                # the exit command mode will reply with 'OK\r', so anything before that is the reply
                if input_chars[-3:] == bytearray([0x4F, 0x4B, 0x0D]):
                    # return anything before the OK
                    return input_chars[:-4]

        # if here means no reply in 1 seconds, which is definitely not right.. return None
        return None

    def check_serial_baud_rate(self):
        """
        check which baud rate is preset in the Xbee module by trying all possible options:
            BD: 0x0000 -> 1200 bps
            BD: 0x0001 -> 2400 bps
            BD: 0x0002 -> 4800 bps
            BD: 0x0003 -> 9600 bps [default]
            BD: 0x0004 -> 19200 bps
            BD: 0x0005 -> 38400 bps
            BD: 0x0006 -> 57600 bps
            BD: 0x0007 -> 115200 bps

        Note that it is unlikely that slower-than-9600 bps is used, so first checking most probably ones

        :return:
        """
        bauds = [9600, 57600, 115200, 38400, 19200, 4800, 2400, 1200]
        counter = 0

        logStr = "WARN: Looking for preset baudrate for the XBee.."
        print(logStr)
        self.logRAWtofile(logStr)

        while counter < len(bauds):
            # close previously opened serial port in order to start a new one with the different baud
            self.serial_port.close()

            # wait guard time
            time.sleep(1.)  # default guard time

            # open new serial with new baud
            logStr = "Checking baud '{}'".format(bauds[counter])
            print(logStr)
            self.logRAWtofile(logStr)
            self.serial_port = Serial(port=self.port, baudrate=bauds[counter])

            # start command mode
            self._write(bytearray("+++".encode()))

            # try to receive
            ok_received = False
            time_req = time.time()
            input_chars = bytearray([])
            while not ok_received:
                if time.time() - time_req > 1.2:
                    # print("ERR: OK not received!")
                    break

                while self.serial_port.inWaiting():
                    input_chars.extend(self.serial_port.read())
                if len(input_chars) >= 3:
                    # note that other messages could have been received while starting the command mode, but nothing
                    # can be received after the command mode is set, which is confirmed by 'OK\r' reply from XBee
                    if input_chars[-3:] == bytearray([0x4F, 0x4B, 0x0D]):
                        ok_received = True
                        return bauds[counter]

            # didn't work.. try next baud
            counter += 1

        # if here means no baud was successful.. error and exit app
        logStr = "ERR: couldn't find preset baud on XBee.. exiting.."
        print(logStr)
        self.logRAWtofile(logStr)

        # force exit
        sys.exit(-1)


# ===============================================================================
#   define methods for Frame-Specific Data Construction
# ===============================================================================
    def setLocalRegistry(self, command, value, frame_ID=0x52):
        return self._setgetLocalRegistry(command, value, frame_ID=frame_ID)

    def getLocalRegistry(self, command, frame_ID=0x52):
        return self._setgetLocalRegistry(command, frame_ID=frame_ID)

    def _setgetLocalRegistry(self, command, value=None, frame_ID=0x52):
        """
        Query or set module parameters on the local device.

        :param command: local AT command as 2 ASCII string
        :param value: if provided, value to assign.
                If not provided, meaning a request
        :param frame_ID: default value 0x52. Change it if you know what you are doing..
        :return: XBee_msg object containing the created message.
                Can be printed using print(_setLocalRegistry(..))
        """
        # create new XB_locAT_OUT object and write to serial
        XBmsg = XB_locAT_OUT(self.params, command, regVal=value, frame_ID=frame_ID)
        if XBmsg.isValid():
            self._write(XBmsg.genFrame())

            # log RAW msg
            self.logRAWtofile(XBmsg)

        return XBmsg

    def setRemoteRegistry(self, destH, destL, command, value, frame_ID=0x01):
        return self._setgetRemoteRegistry(destH, destL, command, value, frame_ID=frame_ID)

    def getRemoteRegistry(self, destH, destL, command, frame_ID=0x01):
        return self._setgetRemoteRegistry(destH, destL, command, frame_ID=frame_ID)

    def _setgetRemoteRegistry(self, destH, destL, command, value=None, frame_ID=0x01):
        """
        Query or set module parameters on a remote device.

        :param command: remote AT command as 2 ASCII string
        :param value: if provided, value to assign.
                If not provided, meaning a request
        :param frame_ID: default value 0x52. Change it if you know what you are doing..
        :return: XBee_msg object containing the created message.
                Can be printed using print(setRemoteRegistry(..))
        """
        self.params['DH'] = destH
        self.params['DL'] = destL

        # create new XB_remAT_OUT object and write to serial
        XBmsg = XB_remAT_OUT(self.params, command, regVal=value, frame_ID=frame_ID)
        if XBmsg.isValid():
            self._write(XBmsg.genFrame())

            # log RAW msg
            self.logRAWtofile(XBmsg)

        return XBmsg

    def sendDataToRemote(self, destH, destL, data, frame_ID=0x01, option=0x00, reserved='fffe'):
        """
        Send data as an RF packet to the specified destination.

        :param destH: high address of the destination XBee
        :param destL: low address of the destination XBee
        :param data: content of the transmit as bytearray
        :param frame_ID: default value 0x01. Change it if you know what you are doing..
        :param option: default value 0x00. can be changed to 0x08 for trace routing
        :param reserved: should be 'FFFE' unless for trace routing = 'FFFF'
        :return: XBee_msg object containing the created message.
                Can be printed using print(sendDataToRemote(..))
        """
        # check data consistency
        if type(data) == str:
            # change it to bytearray
            data = bytearray(data.encode())

        self.params['DH'] = destH
        self.params['DL'] = destL

        # create new XB_RF_OUT object and write to serial
        XBmsg = XB_RF_OUT(self.params, data, frame_ID=frame_ID, option=option, reserved=reserved)
        if XBmsg.isValid():
            self._write(XBmsg.genFrame())

            # log RAW msg
            self.logRAWtofile(XBmsg)

        return XBmsg

    def broadcastData(self, data, frame_ID=0x01, option=0x00, reserved='fffe'):
        """
        Send data as an RF packet to the specified destination.

        :param destH: high address of the destination XBee
        :param destL: low address of the destination XBee
        :param data: content of the transmit as bytearray
        :param frame_ID: default value 0x01. Change it if you know what you are doing..
        :param option: default value 0x00. can be changed to 0x08 for trace routing
        :param reserved: should be 'FFFE' unless for trace routing = 'FFFF'
        :return: XBee_msg object containing the created message.
                Can be printed using print(sendDataToRemote(..))
        """
        destH = '00000000'
        destL = '0000ffff'

        # same as sendDataToRemote() with defined destH and destL
        return self.sendDataToRemote(destH, destL, data, frame_ID=frame_ID, option=option, reserved=reserved)


# ===============================================================================
#   Serial communication with XBee
# ===============================================================================
    def _flush(self):
        """
        Dump all data waiting in the incoming serial port to be sure there is no data upon looking for specified
        responses
        """
        self.serial_port.flush()
        self.serial_port.flushInput()
        self.serial_port.flushOutput()

        while self.serial_port.inWaiting():
            self.serial_port.read()

    def _write(self, msg):
        """
        Send data to serial communication to XBee

        :param msg: DigiMesh frame as bytearray
        :return: None
        """
        self.serial_port.write(msg)

    def readSerial(self):
        """
        Receives data from serial.
        If in API mode, will also checks buffer for potential messages and stacks them into a queue for evaluation.

        :return: list of byte received as bytearray or list of API packets as bytearrays if in API mode
        """
        # read incoming buffer and pack it into the RxStream
        while self.serial_port.inWaiting():
            incoming = self.serial_port.read()
            self.RxBuff.extend(incoming)
            # time.sleep(0.001)

        # if in Transparent Mode, just return everything read and clear the buffer
        if self.params['AP'] == '00':
            data = self.RxBuff
            self.RxBuff = bytearray([])
            return data

        # clear received correct message as API object list
        self.RxMsg = list()

        # split the Rx stream by XBee Start byte (0x7E). OBS: byte 0x7E is stripped away!
        msgs = self.RxBuff.split(bytes(b'\x7E'))

        # add the good messages to the Rx Frames buffer
        self._stack_frame(msgs)

        # hold on to remaining bytes that may have not validated
        if len(self.RxMsg) > 0 and not self.RxMsg[-1].isValid():
            # discard last obj and put msg back in buffer
            self.RxMsg.pop(-1)
            self.RxBuff = msgs[-1][1:]
        elif not XBee_msg.validate(XBee_msg.unescape(msgs[-1]))[0]:
            self.RxBuff = msgs[-1][1:]
        else:
            # clear the buffer
            self.RxBuff = bytearray([])

        return self.RxMsg


# ===============================================================================
#   Operations on received frames
# ===============================================================================
    def _stack_frame(self, msgs):
        """
        Validate incoming messages.  If message
        is valid, stack into inbox of frames to
        be executed
        """
        for msg in msgs:
            # put back previously removed start delimiter
            msg.insert(0, 0x7E)

            # use static methods from XBee_msg class to validate the msg
            msg = XBee_msg.unescape(msg)
            if not XBee_msg.validate(msg)[0]:
                continue

            # create XB_msg object depending on the frame_type
            try:
                # use frame_type info (msg[3]) to get the relative function from APIop dictionary
                recXB = APIop[msg[3]][1](self.params, msg)
                # print(recXB.getHexCmd())
                # check validity
                if recXB.isValid():
                    # log msg
                    self.logRAWtofile(recXB)
                    # if print flag on, then print on screen
                    if APIop[msg[3]][2]:
                        print(recXB)
                # else:
                #     print('failed frame validation on: {0}'.format(''.join('{:02x}'.format(byte) for byte in msg)))
                #     try:
                #         print(msg.decode())
                #     except: pass

                # append object to list of received messages -> note also if verification failed
                self.RxMsg.append(recXB)
            except KeyError:
                print('frame type 0x' + '{:02X}'.format(msg[3]) + ' not recognized/yet not coded')
                # print(''.join('{:02x}'.format(byte) for byte in msg))
                # try:
                #     print(msg.decode())
                # except: pass


# ===============================================================================
#   Custom methods for swarming
# ===============================================================================
#     def swarmTopologicalBroadcast(self):
#         # TODO: here create a function which, before broadcasting, first looks and
#         # finds the neighbors, put a limit on them (topology), and then makes single
#         # communication to them, expecting the ACK.
#         # this is because when using the XBee broadcast, every device sends the info
#         # MT+1 times to every other device within its RF range. Furthermore, since
#         # each device in our project is a router (not endpoint), then each device
#         # will then re-broadcast MT+1 times the same info.
#         # Considering our RF range is now pretty big (~400m) to total communications
#         # initiated by 1 broadcast is huge (MT+1)*n, where n=num devices
#
#         # problem here is however how to know when, if received something, if need to
#         # broadcast or not.. (if it was alr received before)
#
#         return

    def findNeighbors(self, destH, destL):
        """
        XBee provides a feature to discover and report all RF modules found within
        immediate RF range

        :param destH: high address of link receiving device
        :param destL: low address of link receiving device
        :return:
        """
        if destH.upper() == 'LOCAL' or destL.upper() == 'LOCAL':
            print(self.getLocalRegistry('FN'))

            return
        elif destH.upper() == 'GLOBAL' or destL.upper() == 'GLOBAL':
            print('Attempting to broadcast findNeighbors! not allowed :(')
            return

        # check consistency of the input address
        destH = self._checkAddrConsistency(destH)
        destL = self._checkAddrConsistency(destL)
        if not destH or not destL:
            return

        # if address equal to local XBee, then use local registry methods
        if destH.lower() == self.params['SH'] and destL.lower() == self.params['SL']:
            print(self.getLocalRegistry('FN'))

            return
        # if address is for broadcast, then stop! not allowed
        elif destH.lower() == '00000000' and destL.lower() == '0000ffff':
            print('Attempting to broadcast findNeighbors! not allowed :(')
            return

        print(self.getRemoteRegistry(destH, destL, 'FN'))


# ===============================================================================
#   Test Link
# ===============================================================================
    def linkQualityTest(self, senderH, senderL, destH, destL, byteToTest=0x20, iterationsToTest=200):
        """
        XBee provided features, which allows to test the link between the local
        device and a remote one. Note is not possible to broadcast this information

        :param senderH: high address of link starting device
        :param senderL: low address of link starting device
        :param destH: high address of link receiving device
        :param destL: low address of link receiving device
        :param byteToTest: number of bytes to test in each iteration
        :param iterationsToTest: number of iterations for repeating the test.
        :return: None
        """
        # check data consistency
        senderH = self._checkAddrConsistency(senderH)
        if not senderH:
            return
        senderL = self._checkAddrConsistency(senderL)
        if not senderL:
            return
        destH = self._checkAddrConsistency(destH)
        if not destH:
            return
        destL = self._checkAddrConsistency(destL)
        if not destL:
            return

        # set high and low destination address to local address: this is from where to start the linkTest
        self.params['DH'] = senderH
        self.params['DL'] = senderL

        # define test data as bytearray as: destination address, payload size (2bytes), iterations (max 4000)
        testData = bytearray.fromhex(destH) + bytearray.fromhex(destL) \
                   + bytearray.fromhex('{:04x}'.format(byteToTest)) \
                   + bytearray.fromhex('{:04x}'.format(iterationsToTest))
        XBmsg = XB_RFexpl_OUT(self.params, testData, 0xE6, 0xE6, '0014')
        if XBmsg.isValid():
            self._write(XBmsg.genFrame())
            print(XBmsg)
            # print(XBmsg.getHexCmd())

    @staticmethod
    def _checkAddrConsistency(addr):
        """
        check the given address is of type str and length 8.
        If addr is provided as bytearray it is converted to str.

        :param addr: address to check
        :return: the formatted address or None if not correct
        """
        if type(addr) is bytearray and len(addr) == 4:
            return ''.join('{:02x}'.format(byte for byte in addr))
        elif type(addr) is str and len(addr) == 8:
            return addr
        else:
            print("Address must be provided as string, length 8!")
            return None

    def networkDiscover(self):
        """
        XBee provides a feature to discover and report all RF modules found using
        the same 'ID' (Network ID)

        :return:
        """
        print(self.getLocalRegistry('ND'))

    def traceRoute(self, destH, destL):
        """
        Attempt a route tracing when sending data to the defined XBee.
        Not acceptable to trace local XBee or broadcast

        :param destH: high address of link receiving device
        :param destL: low address of link receiving device
        :return:
        """
        if destH.upper() == 'LOCAL' or destH.upper() == 'LOCAL':
            print('Attempting to trace routing the local XBee! not allowed :(')
            return
        elif destH.upper() == 'GLOBAL' or destH.upper() == 'GLOBAL':
            print('Attempting to broadcast trace routing! not allowed :(')
            return

        # check consistency of the input address
        destH = self._checkAddrConsistency(destH)
        destL = self._checkAddrConsistency(destL)
        if not destH or not destL:
            return

        # if address is local or for broadcast, then stop! not allowed
        if destH.lower() == self.params['SH'] and destL.lower() == self.params['SL']:
            print('Attempting to trace routing the local XBee! not allowed :(')
            return
        elif destH.lower() == '00000000' and destL.lower() == '0000ffff':
            print('Attempting to broadcast trace routing! not allowed :(')
            return

        msg = self.sendDataToRemote(destH, destL, bytearray([1, 2, 3]), option=0x08, reserved='ffff')
        # print(msg.getHexCmd())
        print(msg)

# ===============================================================================
#   Log RAW data coming/outgoing from/to XBee
# ===============================================================================
    def logRAWtofile(self, line):
        """
        Write RAW data streams to a file for post-processing and logging
        """
        with open(self.rawLogFileIDstr, 'a') as fileID:
            fileID.write(str(line) + '\n')
            fileID.flush()

# ===============================================================================
#   Establish Print Method
# ===============================================================================
    def __str__(self):

        return "XBee " + str(self.params['SL']) + " Communicating via " + str(self.serial_port)
