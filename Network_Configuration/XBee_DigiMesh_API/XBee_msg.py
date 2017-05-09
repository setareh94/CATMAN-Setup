#!/usr/bin/env python

"""
Containing classes for DigiMesh protocol messages construction.
Using superclass as general class defining basic methods and attributes
Adding children classes for frame-specific data
"""

import datetime     # timestamp all messages (incoming and outgoing)


# authorship info
__author__      = "Francesco Vallegra"
__copyright__   = "Copyright 2016-2017, SUTD"
__license__     = "MIT"


# dictionary to interpret AT response status code
ATstatus = {0: 'OK', 1: 'ERROR', 2: 'invalid command', 3: 'invalid parameter', 4: 'Route not found'}

# dictionary to interpret RF response option code
RFoption = {1: 'toMe', 2: 'broadcast'}

# dictionary to interpret RF status frame code
RFstatus = {0: 'OK', 1: 'MAC ACK failed', 21: 'Invalid dest', 33: 'Network ACK failed', 37: 'Route not found'}

# dictionary to interpret RF discovery status code
RFdiscSt = {0: 'No overhead', 2: 'broadcast'}


# ===============================================================================
#   General class (superclass)
# ===============================================================================
class XBee_msg:
    """
    XBee_message general class for both outgoing and incoming frames

    every object is automatically time-stamped (local time, not UTC) when created
    """

    # create general class prototype
    def __init__(self, XBparams):
        self.XBparams = XBparams

        # immediately timestamp during creation in local time!! (not UTC)
        # self.time_stmp = str(datetime.datetime.now()).split('.')[0]
        self.time_stmp = str(datetime.datetime.now())

        self.length = 0

        self.frame_type = 0x00
        self.data = bytearray()

        self.checksum = 0x00
        self.hexMsg = ''
        self.valid = True

    # ===============================================================================
    #   Pack the message content with the DigiMesh header and trail
    def _genDigiMeshFrame(self, frameData):
        """
        DigiMesh frame is structured as follow (in bytes):
        - 0         : Start Delimiter [0x7E]
        - 1-2       : Length n, defined as the actual message content, starting from byte 3, not including CRC
        - 3-(3+n-1) : Frame-Specific Data
        - (3+n)     : Checksum (2's complement)

        :param frameData: Frame-Specific data, given as bytearray
        :return: DigiMesh compliant full frame, as bytearray
        """

        # define frame header
        strt_delim = '7E'                                   # = '{:02X}'.format(0x7E)
        self.length = len(frameData)
        header = strt_delim + '{:04X}'.format(self.length)  # length is defined as 2 bytes

        # Calculate Check Sum and format frame (as 2's complements)
        self.checksum = 0xFF - ((sum(frameData)) & 0xFF)

        # Sandwich frame with header, frameData, and checksum
        frame = bytearray.fromhex(header) + frameData
        frame.append(self.checksum)

        # Note we are using XBee series 1, which is limiting the actual frame size to 100bytes.
        if len(frameData) >= 100:
            print('XBee frame larger than 100bytes! XBee Series 1 does not support this..')

        return frame

    # ===============================================================================
    #   Frame Validation
    def isValid(self):
        """
        :return: if the validation process succeeded upon creation of the object, return True
        """
        return self.valid

    @staticmethod
    def validate(msg):
        """
        Verify Checksum and Length in received
        message against calculated based on
        actual message content

        :param msg: full frame message obtained, given as bytearray
        :return: None
        """
        valid = True

        if not msg or len(msg) < 4:
            return False, -1, -1

        checksum = msg[-1]
        length = int(''.join('{:02X}'.format(byte) for byte in msg[1:3]), 16)
        # try:
        #     # here works for pyton 3 only
        #     length = int.from_bytes(msg[1:3], byteorder='big', signed=False)
        # except Exception:
        #     length = int(''.join('{:02X}'.format(byte) for byte in msg[1:3]), 16)

        validlen = len(msg[3:-1])
        validsum = 0xFF - ((sum(msg[3:-1])) & 0xFF)

        # print('length: ' + str(self.length) + '; ' + str(validlen))
        # print('checksum: ' + str(self.checksum) + '; ' + str(validsum))

        # check sanity of computed Length and Checksum with the one in the message
        if (checksum != validsum) or (length != validlen):
            valid = False

        return valid, length, checksum

    # ===============================================================================
    #   Add/Remove Escaping Sequences
    @staticmethod
    def _escape(msg):
        """
        Escape reserved characters to ensure accurate
        message transmission and reception
        """
        reserved = bytearray('\x7E\x7D\x11\x13'.encode())
        escaped = bytearray()
        escaped.append(msg[0])

        for byte in msg[1:]:

            if byte in reserved:
                escaped.append(0x7D)
                escaped.append(byte ^ 0x20)
            else:
                escaped.append(byte)

        return escaped

    @staticmethod
    def unescape(msg):
        """
        Retrieve unescaped message from escaped message
        in order to understand intended message
        """
        skip = False
        unescaped = bytearray()

        for i in range(len(msg)):

            if not skip and msg[i] is 0x7D:

                if not (i + 1) >= len(msg):
                    unescaped.append(msg[i + 1] ^ 0x20)
                    skip = True

            elif not skip:
                unescaped.append(msg[i])
            else:
                skip = False

        return unescaped

    # ===============================================================================
    #   Stringify message and get method
    def getHexCmd(self):
        return self.hexMsg

    def _hexStr(self, frame):
        self.hexMsg = ''.join('{:02X}'.format(byte) for byte in frame)


# ===============================================================================
#   Child class: OUT - local XBee set/get AT (registries) commands
# ===============================================================================
class XB_locAT_OUT(XBee_msg):
    """
    Query or set parameters on the local XBee
    """

    def __init__(self, XBparams, ATcmd, regVal=None, frame_ID=0x52):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x08
        self.frame_ID = frame_ID

        # check ATcmd is 2bytes ASCII
        if type(ATcmd) != str or len(ATcmd) != 2:
            print("ATcmd '{0}' should be a 2 byte ASCII string!", format(str(ATcmd)))
            self.valid = False
            return
        self.ATcmd = ATcmd

        # make sure regVal is "understandable"
        self.reg_value = None
        if regVal is not None:
            # note that data can be numbers, string, or bytearray
            if type(regVal) == bytearray:
                # then it is alr in the correct format
                self.reg_value = regVal
            elif type(regVal) == str:
                self.reg_value = bytearray(regVal)
            elif type(regVal) == int:
                if regVal > 65535:
                    regVal = '{:08X}'.format(regVal)
                if regVal > 255:
                    regVal = '{:04X}'.format(regVal)
                else:
                    regVal = '{:02X}'.format(regVal)
                self.reg_value = bytearray.fromhex(regVal)
            else:
                print('Uncoded type(regVal): {0}'.format(type(regVal)))
                self.valid = False
                return

    def _genFrameData(self):
        """
        Frame-specific Data Construct for 'AT Command' (0x08):
            Frame Type (0x08)
            Frame ID (0x52) -> actually can be whatever but 0
            AT Command (0xXX) - First letter
                       (0xXX) - Second letter
            Parameter Value (optional)

        :return: bytearray with frame-specific data
        """
        # create content of the message
        frameData = bytearray([self.frame_type, self.frame_ID]) + bytearray(self.ATcmd.encode())

        # is the registry value is provided, append it
        if self.reg_value is not None:
            value = self.reg_value
            frameData += value

        return frameData

    def genFrame(self):
        """
        Generate DigiMesh compliant full frame, by first creating the Frame-specific data
        :return: full frame in bytearray
        """
        # generate frame-specific data
        frameData = self._genFrameData()

        # call parent function to create the complete frame (as bytearray)
        frame = self._genDigiMeshFrame(frameData)

        # OBS: never escape-sequence local msg
        return frame

    def getHexCmd(self):
        # create hex string of the command, having already provided all the information
        self._hexStr(self.genFrame())

        return self.hexMsg

    def __str__(self):
        if self.reg_value is not None:
            return "{0} OUT (addr:  local  ) Set registry '{1}' to '{2}'".format(self.time_stmp[:-3], self.ATcmd,
                str(''.join('{:02X}'.format(byte) for byte in self.reg_value)))

        return "{0} OUT (addr:  local  ) Get '{1}' registry".format(self.time_stmp[:-3], self.ATcmd)


# ===============================================================================
#   Child class: OUT - remote XBee set/get AT (registries) commands
# ===============================================================================
class XB_remAT_OUT(XBee_msg):
    """
    Query or set parameters on the remote XBee
    """

    def __init__(self, XBparams, ATcmd, regVal=None, frame_ID=0x01, applyChanges=True):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x17
        self.frame_ID = frame_ID

        # destination address is contained in DH and DL params
        self.destAddrHigh = XBparams['DH']
        self.destAddrLow = XBparams['DL']

        # if want to apply changes immediately
        self.applyCh = 0x00
        if applyChanges:
            self.applyCh = 0x02

        # check ATcmd is 2bytes ASCII
        if type(ATcmd) != str or len(ATcmd) != 2:
            print("ATcmd '{0}' should be a 2 byte ASCII string!", format(str(ATcmd)))
            self.valid = False
            return
        self.ATcmd = ATcmd

        # make sure regVal is "understandable"
        self.reg_value = None
        if regVal is not None:
            # note that data can be numbers, string, or bytearray
            if type(regVal) == bytearray:
                # then it is alr in the correct format
                self.reg_value = regVal
            elif type(regVal) == str:
                self.reg_value = bytearray(regVal)
            elif type(regVal) == int:
                if regVal > 65535:
                    regVal = '{:08X}'.format(regVal)
                if regVal > 255:
                    regVal = '{:04X}'.format(regVal)
                else:
                    regVal = '{:02X}'.format(regVal)
                self.reg_value = bytearray.fromhex(regVal)
            else:
                print('Uncoded type(regVal): {0}'.format(type(regVal)))
                self.valid = False
                return

    def _genFrameData(self):
        """
        Frame-specific Data Construct for 'Remote Command Request' (0x17):
            Frame Type (0x17)
            Frame ID (0x01)
            64-bit Destination Address, high (DH) and low (DL)
            16-bit Destination Network Address (0xFFFE if address unknown or sending broadcast)
            Option (0x02) - Apply changes
            AT Command (0xXX) - First letter
                       (0xXX) - Second letter
            Parameter Value (optional)

        :return: bytearray with frame-specific data
        """
        # create content of the message
        frameData = bytearray([self.frame_type, self.frame_ID]) \
                    + bytearray.fromhex(self.destAddrHigh) \
                    + bytearray.fromhex(self.destAddrLow) \
                    + bytearray([0xFF, 0xFE]) \
                    + bytearray([self.applyCh]) \
                    + bytearray(self.ATcmd.encode())

        # is the registry value is provided, append it
        if self.reg_value is not None:
            value = bytearray.fromhex(self.reg_value)
            frameData += value

        return frameData

    def genFrame(self):
        # generate frame-specific data
        frameData = self._genFrameData()

        # call parent function to create the complete frame (as bytearray)
        frame = self._genDigiMeshFrame(frameData)

        # use escape sequence if API mode is 2
        if self.XBparams['AP'] == '02':
            frame = self._escape(frame)

        return frame

    def getHexCmd(self):
        # create hex string of the command, having already provided all the information
        self._hexStr(self.unescape(self.genFrame()))

        return self.hexMsg

    def __str__(self):
        if self.reg_value is not None:
            return "{0} OUT (addr: {1}) Set registry '{2}' to '{3}'".format(self.time_stmp[:-3], self.destAddrLow,
                                                                            self.ATcmd, str(self.reg_value))

        return "{0} OUT (addr: {1}) Get '{2}' registry".format(self.time_stmp[:-3], self.destAddrLow, self.ATcmd)


# ===============================================================================
#   Child class: OUT - send RF data to remote XBee
# ===============================================================================
class XB_RF_OUT(XBee_msg):
    """
    Send data as an RF packet to the specified destination.
    """

    def __init__(self, XBparams, data, frame_ID=0x01, radius=0x00, option=0x00, reserved='FFFE'):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x10
        self.frame_ID = frame_ID

        # destination address is contained in DH and DL params
        self.destAddrHigh = XBparams['DH']
        self.destAddrLow = XBparams['DL']

        # reserved
        if type(reserved) is bytearray and len(reserved) == 2:
            # no need to do anything
            self.reserved = reserved
        elif type(reserved) is str and len(reserved) == 4:
            self.reserved = bytearray.fromhex(reserved)
        else:
            print('reserved type wrong. Should be either bytearray (2 bytes) ot string (4 bytes)')
            self.valid = False
            return

        # communication radius [0: maximum hop]
        self.radius = radius
        # option [0: no ACK; 1: no Route Discovery]
        self.option = option

        # make sure data is in the correct format -> here expected as bytearray
        if type(data) != bytearray:
            print('Content of message should be formatted as bytearray!')
            self.valid = False
            return
        self.data = data

    def _genFrameData(self):
        """
        Frame-specific Data Construct for 'RF transmit' (0x10):
            Frame Type (0x10)
            Frame ID (0x01)
            64-bit Destination Address, high (DH) and low (DL)
            16-bit Destination Network Address (0xFFFE if address unknown or sending broadcast)
            Broadcast Radius
            Options
            Data -> as bytearray

        :return: bytearray with frame-specific data
        """
        # create content of the message
        frameData = bytearray([self.frame_type, self.frame_ID]) \
                    + bytearray.fromhex(self.destAddrHigh) \
                    + bytearray.fromhex(self.destAddrLow) \
                    + self.reserved \
                    + bytearray([self.radius, self.option]) \
                    + self.data

        return frameData

    def genFrame(self):
        # generate frame-specific data
        frameData = self._genFrameData()

        # call parent function to create the complete frame (as bytearray)
        frame = self._genDigiMeshFrame(frameData)

        # use escape sequence if API mode is 2
        if self.XBparams['AP'] == '02':
            frame = self._escape(frame)

        return frame

    def getHexCmd(self):
        # create hex string of the command, having already provided all the information
        self._hexStr(self.unescape(self.genFrame()))

        return self.hexMsg

    def __str__(self):
        addr = self.destAddrLow
        if self.destAddrHigh == '00000000' and (self.destAddrLow == '0000FFFF' or self.destAddrLow == '0000ffff'):
            addr = ' GLOBAL '

        return "{0} OUT (addr: {1}) data: hex'{2}'".format(self.time_stmp[:-3], addr,
                                                           ''.join('{:02X}'.format(byte) for byte in self.data))


# ===============================================================================
#   Child class: OUT - send explicit RF data to remote XBee
# ===============================================================================
class XB_RFexpl_OUT(XBee_msg):
    """
    Send data as an explicit RF packet to the specified destination.
    """

    def __init__(self, XBparams, data, srcEP, destEP, clusterID, profileID='C105',
                 frame_ID=0x01, radius=0x00, option=0x00):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x11
        self.frame_ID = frame_ID

        # destination address is contained in DH and DL params
        self.destAddrHigh = XBparams['DH']
        self.destAddrLow = XBparams['DL']

        # endpoints
        self.srcEP = srcEP
        self.destEP = destEP

        # cluster ID
        if type(clusterID) == bytearray:
            # then it is alr in the correct format
            if len(clusterID) != 2:
                print('clusterID value {0} should be 2 bytes!'.format(clusterID))
                self.valid = False
                return
            self.clusterID = clusterID
        elif type(clusterID) == str:
            if len(clusterID) != 4:
                print('clusterID value {0} should be 2 bytes (4 hex string)!'.format(clusterID))
                self.valid = False
                return
            self.clusterID = bytearray.fromhex(clusterID)
        elif type(clusterID) == int:
            if clusterID > 65535:
                print('clusterID value {0} exceeding 16bit variable!'.format(clusterID))
                self.valid = False
                return
            self.clusterID = bytearray.fromhex('{:04X}'.format(clusterID))
        else:
            print('Uncoded type(clusterID): {0}... Please use bytearray, str or int'.format(type(clusterID)))
            self.valid = False
            return

        # profile ID
        if type(profileID) == bytearray:
            # then it is alr in the correct format
            if len(profileID) != 2:
                print('profileID value {0} should be 2 bytes!'.format(profileID))
                self.valid = False
                return
            self.profileID = profileID
        elif type(profileID) == str:
            if len(profileID) != 4:
                print('profileID value {0} should be 2 bytes (4 hex string)!'.format(profileID))
                self.valid = False
                return
            self.profileID = bytearray.fromhex(profileID)
        elif type(profileID) == int:
            if profileID > 65535:
                print('profileID value {0} exceeding 16bit variable!'.format(profileID))
                self.valid = False
                return
            self.profileID = bytearray.fromhex('{:04X}'.format(profileID))
        else:
            print('Uncoded type(profileID): {0}... Please use bytearray, str or int'.format(type(profileID)))
            self.valid = False
            return

        # communication radius [0: maximum hop]
        self.radius = radius
        # option [0: no ACK; 1: no Route Discovery]
        self.option = option

        # make sure data is in the correct format -> here expected as bytearray
        if type(data) != bytearray:
            print('Content of message should be formatted as bytearray!')
            self.valid = False
            return
        self.data = data

    def _genFrameData(self):
        """
        Frame-specific Data Construct for 'RF transmit' (0x10):
            Frame Type (0x10)
            Frame ID (0x01)
            64-bit Destination Address, high (DH) and low (DL)
            16-bit Destination Network Address (0xFFFE if address unknown or sending broadcast)
            Source-Endpoint
            Destination-Endpoint
            Cluster ID (2 bytes)
            Profile ID (2 bytes)
            Broadcast Radius
            Options
            Data -> as bytearray

        :return: bytearray with frame-specific data
        """
        # create content of the message
        frameData = bytearray([self.frame_type, self.frame_ID]) \
                    + bytearray.fromhex(self.destAddrHigh) \
                    + bytearray.fromhex(self.destAddrLow) \
                    + bytearray([0xFF, 0xFE]) \
                    + bytearray([self.srcEP, self.destEP]) \
                    + self.clusterID + self.profileID \
                    + bytearray([self.radius, self.option]) \
                    + self.data

        return frameData

    def genFrame(self):
        # generate frame-specific data
        frameData = self._genFrameData()

        # call parent function to create the complete frame (as bytearray)
        frame = self._genDigiMeshFrame(frameData)

        # use escape sequence if API mode is 2
        if self.XBparams['AP'] == '02':
            frame = self._escape(frame)

        return frame

    def getHexCmd(self):
        # create hex string of the command, having already provided all the information
        self._hexStr(self.unescape(self.genFrame()))

        return self.hexMsg

    def __str__(self):
        addr = self.destAddrLow.lower()
        if addr == self.XBparams['SL'].lower():
            addr = ' local  '
        elif self.destAddrHigh == '00000000' and addr == '0000ffff':
            addr = ' GLOBAL '

        return "{0} OUT (addr: {1}) explicit transmit; data: hex'{2}'".format(self.time_stmp[:-3], addr,
            ''.join('{:02X}'.format(byte) for byte in self.data))


# ===============================================================================
#   Child class: IN - local XBee set/get AT (registries) response
# ===============================================================================
class XB_locAT_IN(XBee_msg):
    """
    Decode AT (registry) commands from local XBee
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x88
        self.frame_ID = 0x01
        self.ATcmd = ''
        self.cmdStatus = 0x00
        self.reg_value = None

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'AT Command response' (0x88):
            Frame Type (0x88)
            Frame ID (0x01) -> actually can be whatever but 0
            AT Command (0xXX) - First letter
                       (0xXX) - Second letter
            cmdStatus
            Parameter Value (optional)

        :return: none
        """
        self.frame_ID = frame[4]
        self.ATcmd = frame[5:7].decode("ascii")
        self.cmdStatus = frame[7]

        # if length is greater than 9bytes, we have data
        if len(frame) > 9:
            self.data = frame[8:-1]
            self.reg_value = ''.join('{:02X}'.format(byte) for byte in frame[8:-1])

            # set params[AT] to the received value -> note this will change the original too in XBee_API class!!
            try:
                self.XBparams[self.ATcmd] = self.reg_value.lower()
            except KeyError:
                pass

    def __str__(self):
        if self.reg_value is None:
            try:
                strin = "{0}  IN (addr:  local  ) Registry '{1}' has been set; [{2}]".format(self.time_stmp[:-3],
                    self.ATcmd, ATstatus[self.cmdStatus])
            except KeyError:
                strin = "{0}  IN (addr:  local  ) Registry '{1}' has been set; [status: {2}]".format(
                    self.time_stmp[:-3], self.ATcmd, self.cmdStatus)
            return strin

        try:
            strin = "{0}  IN (addr:  local  ) Registry '{1}' = '{2}'; [{3}]".format(self.time_stmp[:-3],
                self.ATcmd, self.reg_value, ATstatus[self.cmdStatus])
        except KeyError:
            strin = "{0}  IN (addr:  local  ) Registry '{1}' = '{2}'; [status: {3}]".format(self.time_stmp[:-3],
                self.ATcmd, self.reg_value, self.cmdStatus)
        return strin


# ===============================================================================
#   Child class: IN - remote XBee set/get AT (registries) response
# ===============================================================================
class XB_remAT_IN(XBee_msg):
    """
    Decode AT (registry) commands from remote XBee
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x97
        self.frame_ID = 0x55
        self.ATcmd = ''

        self.destAddrHigh = ''
        self.destAddrLow = ''

        self.cmdStatus = 0x00
        self.reg_value = None

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'remote AT Command response' (0x97):
            Frame Type (0x97)
            Frame ID (0x55) -> actually can be whatever but 0
            64-bit Destination Address, high (DH) and low (DL)
            16-bit reserved (0xFFFE)
            AT Command (0xXX) - First letter
                       (0xXX) - Second letter
            cmdStatus
            Parameter Value (optional)

        :return: none
        """
        self.frame_ID = frame[4]
        self.destAddrHigh = ''.join('{:02x}'.format(byte) for byte in frame[5:9])
        self.destAddrLow = ''.join('{:02x}'.format(byte) for byte in frame[9:13])
        self.ATcmd = frame[15:17].decode("ascii")
        self.cmdStatus = frame[17]

        # if length is greater than 9bytes, we have data
        if len(frame) > 19:
            self.data = frame[18:-1]
            self.reg_value = ''.join('{:02X}'.format(byte) for byte in frame[18:-1])

    def __str__(self):
        if self.reg_value is None:
            try:
                strin = "{0}  IN (addr: {1}) Registry '{2}' has been set; [{3}]".format(self.time_stmp[:-3],
                    self.destAddrLow, self.ATcmd, ATstatus[self.cmdStatus])
            except KeyError:
                strin = "{0}  IN (addr: {1}) Registry '{2}' has been set; [status: {3}]".format(self.time_stmp[:-3],
                    self.destAddrLow, self.ATcmd, self.cmdStatus)
            return strin

        try:
            strin = "{0}  IN (addr: {1}) Registry '{2}' = '{3}'; [{4}]".format(self.time_stmp[:-3], self.destAddrLow,
                self.ATcmd, self.reg_value, ATstatus[self.cmdStatus])
        except KeyError:
            strin = "{0}  IN (addr: {1}) Registry '{2}' = '{3}'; [status : {4}]".format(self.time_stmp[:-3],
                self.destAddrLow, self.ATcmd, self.reg_value, self.cmdStatus)
        return strin


# ===============================================================================
#   Child class: IN - get RF data from remote XBee
# ===============================================================================
class XB_RF_IN(XBee_msg):
    """
    Decode RF frame from remote XBee
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x90
        self.frame_ID = 0x00

        self.destAddrHigh = ''
        self.destAddrLow = ''

        self.option = 0x01  # [1: toMe; 2: broadcast]

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'remote RF frame response' (0x90):
            Frame Type (0x90)
            Frame ID (0x00)
            64-bit Destination Address, high (DH) and low (DL)
            16-bit reserved (0xFFFE)
            Option [1: toMe; 2: broadcast]
            Data

        :return: none
        """
        self.frame_ID = frame[4]
        # OBS: here the high addr is just 3bytes (last)!!
        self.destAddrHigh = ''.join('{:02x}'.format(byte) for byte in frame[5:8])
        self.destAddrLow = ''.join('{:02x}'.format(byte) for byte in frame[8:12])
        self.option = frame[14] & 0x02  # mask is necessary, cause other bits are reserved
        self.data = frame[15:-1]

    def __str__(self):
        try:
            strin = "{0}  IN (addr: {1}) data: hex'{2}'; [{3}]".format(self.time_stmp[:-3], self.destAddrLow,
                                ''.join('{:02X}'.format(byte) for byte in self.data), RFoption[self.option])
        except KeyError:
            strin = "{0}  IN (addr: {1}) data: hex'{2}'; [status: {3}]".format(self.time_stmp[:-3], self.destAddrLow,
                ''.join('{:02X}'.format(byte) for byte in self.data), self.option)

        return strin


# ===============================================================================
#   Child class: IN - get explicit RF data from remote XBee
# ===============================================================================
class XB_RFexpl_IN(XBee_msg):
    """
    Decode explicit RF frame from remote XBee
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x91

        self.destAddrHigh = ''
        self.destAddrLow = ''

        self.srcEP = 0x00
        self.destEP = 0x00

        self.clusteID = ''
        self.profileID = ''

        self.option = 0x01  # [1: toMe; 2: broadcast]

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'remote RF frame response' (0x90):
            Frame Type (0x90)
            Frame ID (0x00)
            64-bit Destination Address, high (DH) and low (DL)
            16-bit reserved (0xFFFE)
            Option [1: toMe; 2: broadcast]
            Data

        :return: none
        """
        self.destAddrHigh = ''.join('{:02x}'.format(byte) for byte in frame[4:8])
        self.destAddrLow = ''.join('{:02x}'.format(byte) for byte in frame[8:12])
        self.srcEP = frame[14]
        self.destEP = frame[15]
        self.clusteID = frame[16:18]
        self.profileID = frame[18:20]
        self.option = frame[20] & 0x02  # mask is necessary, cause other bits are reserved
        self.data = frame[21:-1]

    def __str__(self):
        addr = self.destAddrLow.lower()
        if addr == self.XBparams['SL'].lower():
            addr = ' local  '
        try:
            strin = "{0}  IN (addr: {1}) explicit transmit data: hex'{2}'; [{3}]".format(self.time_stmp[:-3],
                addr, ''.join('{:02X}'.format(byte) for byte in self.data), RFoption[self.option])
        except KeyError:
            strin = "{0}  IN (addr: {1}) explicit transmit data: hex'{2}'; [status: {3}]".format(self.time_stmp[:-3],
                addr, ''.join('{:02X}'.format(byte) for byte in self.data), self.option)

        return strin


# ===============================================================================
#   Child class: IN - RF transmit received
# ===============================================================================
class XB_RFstatus_IN(XBee_msg):
    """
    RF status frame from XBee network
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x8B
        self.frame_ID = 0x47

        self.tries = 0x00       # num of tries before it got completed
        self.status = 0x00
        self.discovSt = 0x00

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'RF status frame' (0x8B):
            Frame Type (0x8B)
            Frame ID (0x47)
            16-bit reserved (0xFFFE)
            Transmit tries
            Transmit status
            Discovery status

        :return: none
        """
        self.frame_ID = frame[4]
        self.tries = frame[7]
        self.status = frame[8]
        self.discovSt = frame[9]

    def __str__(self):
        try:
            strin = "{0}  IN (addr: network ) ACK #tries: {1}; [{2}]; [{3}]".format(self.time_stmp[:-3],
                str(self.tries), RFdiscSt[self.discovSt], RFstatus[self.status])
        except KeyError:
            strin = "{0}  IN (addr: network ) ACK #tries: {1}; [discovery status: {2}]; " \
                "[status: {3}]".format(self.time_stmp[:-3], str(self.tries), str(self.discovSt), str(self.status))

        return strin


# ===============================================================================
#   Child class: IN - RF route information received
# ===============================================================================
class XB_RouteInfo_IN(XBee_msg):
    """
    RF route information frame from XBee network
    """

    def __init__(self, XBparams, frame):
        # take attributes already defined for the general class
        XBee_msg.__init__(self, XBparams)

        self.frame_type = 0x8D
        self.sourceEve = 0x12

        self.time = bytearray()
        self.destAddr = ''
        self.srcAddr = ''
        self.responderAddr = ''
        self.receiverAddr = ''

        # if escape sequence used in the msg, remove it (if not, then nothing is done)
        frameun = self.unescape(frame)

        # validate frame
        self.valid, self.length, self.checksum = self.validate(frameun)

        # convert input from bytearray to hex str
        self._hexStr(frameun)

        # decode frame
        if self.valid:
            self.decodeFrame(frameun)

    def decodeFrame(self, frame):
        """
        Frame-specific Data Construct for 'RF status frame' (0x8B):
            Frame Type (0x8B)
            Frame ID (0x47)
            16-bit reserved (0xFFFE)
            Transmit tries
            Transmit status
            Discovery status

        :return: none
        """
        self.sourceEve = frame[4]
        self.time = frame[6:10]
        self.destAddr = ''.join('{:02x}'.format(byte) for byte in frame[13:21])
        self.srcAddr = ''.join('{:02x}'.format(byte) for byte in frame[21:29])
        self.responderAddr = ''.join('{:02x}'.format(byte) for byte in frame[29:37])
        self.receiverAddr = ''.join('{:02x}'.format(byte) for byte in frame[37:45])

    def __str__(self):
        return "{0}  IN (addr: {1}) Route Info '{2}' to '{3}'; receiver: {4}".format(self.time_stmp[:-3],
            self.responderAddr[8:], self.srcAddr[8:], self.destAddr[8:], self.receiverAddr[8:])
