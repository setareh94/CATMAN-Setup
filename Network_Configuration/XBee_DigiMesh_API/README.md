# XBee_DigiMesh_API
Python implementation for interfacing a computer/raspberry Pi/beagleBone to any XBee S1 module (DigiMesh).
This API supports both AT (transparent communication) and API mode (either with or without escaping sequence).

For the API mode, all message types are coded as classes, children of parent class XBee_msg which includes shared methods.


## Usage
This implementation allows to reprogram an XBee module **without knowing any of the configuration initially flashed inside**.

If it's not known the serial port to use for connecting to the XBee module, leaving the `port` argument as `None` will trigger the call to `XB_Finder.py`, which looks for possible valid instances of serial communication devices.
`XB_Finder` method has been tested on Mac, Windows and Linux operating systems.

If the baud rate to use is different from the one used by the module, a method will check all the possible bauds to first find which baud to use for communicating with the module and then change it to the new one.

It is possible to use more than one XBee module at the same time; if so it is however required to input the `port` argument, as the `XB_Finder` will only use the first available instance.

### Create XBee object
Before using any other methods, a XBee API object must be created.

It is possible to configure some XBee registries by passing the following parameters:
- `port`: serial port (if not provided the XB_Finder method is called to find a possible XBee serial instance from the
system - tested on Mac, Linux and Windows);
- `baud`: baud rate of the serial communication (default: `9600`);
- `ID`: Network ID (default: `0x7FFF`);
- `AP`: API Mode (default: `0x02`, API mode with escaping sequence enabled);
- `CE`: Routing/Message mode (default: `0x00`, Router mode - relaying all incoming messages);
- `NO`: Network Discovery Options (default: `0x04`, appended RSSI to network/neighbor discovery
replies).
If any of these parameters is not provided, the default value is used.
Note that the default value may be different from the factory reset. Note also that when using the XBee for the first time, it is mandatory to first set it as AP = 2 otherwise no communication is possible by using the provided interface.

A possible, basic example can be:
```
from XBee_API import XBee_module
XB = XBee_module()
```

If the XBee module was found in the list of serial ports available, the XBee is initialized. If no XBee
Module can be found, an error is raised.

A different example setting up the XBee as EndPoint (no message relaying) in Transparent Mode with baud 57600 can be:
```
from XBee_API import XBee_module
XB = XBee_module(baud=57600, AP=0, CE=2)
```

### Reading and Writing: Threading advisable
This API does not provide any threaded implementation as it is expected a threaded implementation from the user, dependent on how this API is used.
The user can create a separate thread which cyclically calls the `readSerial()` method.

An example is provided in files `example_APImode2.py` and `example_TransparentMode.py`, which use threading on methods defined in file `read_comm.py`.

The threadable method `read_comm(xbee_obj)` in file `read_comm.py` is smartly using the _select_ option on the serial port which reacts as a hardware interrupt, blocking the execution of the thread till something is received (or sent) up to a maximum of 10 seconds. This allow a much less burden on the CPU but can only be used on Unix system (linux, mac, SBC running unix systems). For Windows systems it was instead implemented a read every 100ms.


## API Mode Features
This implementation is including all the main features described in the DigiMesh API:
- [x] setLocalRegistry()
- [x] getLocalRegistry()
- [x] setRemoteRegistry()
- [x] getRemoteRegistry()
- [x] sendDataToRemote()
- [x] broadcastData()
- [x] readSerial()

also including some more specific and usually not implemented features:
- [x] networkDiscover()
- [x] findNeighbors()
- [x] traceRoute()
- [x] linkQualityTest()


### setLocalRegistry()
Method used for setting a registry in the local XBee Device.
This method requires the following parameters:
- `command`: local AT command as 2 ASCII string;
- `value`: value to assign to the AT command;
- `frame_ID` (default: `0x52`): can be set differently if mission specific.

A possible example can be:
```
XB.setLocalRegistry(’AP’, 0x02)
```

Note that the registry value can be expressed also as hex string (`’02’`) or as bytearray (`bytearray([0x02])`).
The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:43:22.871 OUT (addr: local ) Set registry ’AP’ to ’02’
```

### getLocalRegistry()
Method used for getting a registry in the local XBee Device.
This method requires the following parameters:
- `command`: local AT command as 2 ASCII string;
- `frame_ID` (default: `0x52`): can be set differently if mission specific.

A possible example can be:
```
XB.getLocalRegistry(’ID’)
```

The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:43:23.428 OUT (addr: local ) Get ’ID’ registry
```

### setRemoteRegistry()
Method used for setting a registry to a remote XBee Device.
This method requires the following parameters:
- `destH`: high address of the remote device as a hex string;
- `destL`: low address of the remote device as a hex string;
- `command`: local AT command as 2 ASCII string;
- `value`: value to assign to the AT command;
- `frame_ID` (default: `0x52`): can be set differently if mission specific.

A possible example can be:
```
XB.setRemoteRegistry(’0013a200’, ’40e44b94’, ’AP’, 0x02)
```

Note that the registry value can be expressed also as string (`’02’`) or as bytearray (`bytearray([0x02])`).
The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:43:22.871 OUT (addr: 40e44b94) Set registry ’AP’ to ’02’
```


### getRemoteRegistry()
Method used for getting a registry to a remote XBee Device.
This method requires the following parameters:
- `destH`: high address of the remote device as a hex string;
- `destL`: low address of the remote device as a hex string;
- `command`: local AT command as 2 ASCII string;
- `frame_ID` (default: `0x01`): can be set differently if mission specific.

A possible example can be:
```
XB.getRemoteRegistry(’0013a200’, ’40e44b94’, ’ID’)
```

The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:43:23.428 OUT (addr: 40e44b94) Get ’ID’ registry
```

###  sendDataToRemote()
Method used for sending data to a remote XBee Device.
This method requires the following parameters:
- `destH`: high address of the remote device as a hex string;
- `destL`: low address of the remote device as a hex string;
- `data`: data to send, formatted as bytearray;
- `frame_ID` (default: `0x01`): can be set differently if mission specific;
- `option` (default: `0x00`): set to 0x08 for Route Tracing;
- `reserved` (default: `0xFFFE`): set to `0xFFFF` for Route Tracing.

A possible example can be:
```
data = bytearray([0x01, 0x02, 0x03])
XB.sendDataToRemote(’0013a200’, ’40e44b94’, data)
```
Note that the data can be formatted as bytearray or as string.

The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:44:23.563 OUT (addr: 40e44b94) data: hex’010203’
```

###  broadcastData()
Method used for broadcasting data to all XBee Devices in the Network.
This method requires the following parameters:
- `data`: data to send, formatted as bytearray;
- `frame_ID` (default: `0x01`): can be set differently if mission specific;
- `option` (default: `0x00`): set to 0x08 for Route Tracing;
- `reserved` (default: `0xFFFE`): set to `0xFFFF` for Route Tracing.

A possible example can be:
```
data = "hello"
XB.sendDataToRemote(data)
```
Note that the data can be formatted as bytearray or as string.

The method will generate and send the created DigiMesh frame to the serial communication.

It outputs the created XBee message object, which - for instance - can be then printed in the form:
```
2016-07-04 12:44:23.563 OUT (addr:  GLOBAL ) data: hex’68656C6C6F’
```

### readSerial()
Method used for reading data from the serial communication with the local XBee. 
Note that this function only reads until data are inside the serial buffer. 
The readSerial() method should be called iteratively at fast rates.

This method requires no parameters.

The user can get messages sent in transparent mode as:
```
xbee_msg = XB.readSerial()
if xbee_msg:
    print(xbee_msg)
```


___
If using the **API mode** (with or without escaping chars), the data read from the serial buffer is continuously appended in a local buffer.
The local buffer is split in one or several frames by using the DigiMesh start delimiter character 0x7E.
A XBee msg object is created given each frame by using the `frame_type`; if the validation procedure is successful, the frame is removed from the local buffer and the created object is appended to a local
list containing all the received messages.

The received-message list is then returned as output of the readSerial() method and will be emptied at the next call of readSerial() method.

The user can extract each object using:
```
xbee_msg_list = XB.readSerial()
while xbee_msg_list:
    XBmsg = xbee_msg_list.pop(0)
```
It is now possible to recognize each message by `XBmsg.frame_type`. For instance, if `frame_type` = `0x90`, it is possible to access the RF data by using `XBmsg.data` (in bytearray).


## XBee Testing Methods
The following methods are provided by the DigiMesh API [RD1], with recommendation to use them for test purposes only. 
The reason is that they could potentially fail, giving misleading values if not properly used or taking considerable amount of time for real-time implementations.

### networkDiscover()
The Network Discovery feature allows to query each XBee module sharing the same Network ID and within RF range of at least one other XBee, no matter how many hops are needed to reach every individual in the network.
The DigiMesh API provides a registry for defining the maximum time for waiting for a reply to the Network Discovery command; default value is 13 seconds. It is advised to higher up this value in case of large network.
Because of this reason, this feature cannot be used for real-time implementations.

The Network Discovery command could be potentially sent to a remote XBee module, but the reply would be the same, so it was implemented for addressing the local XBee only.

No input parameters are needed and no output parameter.

By sending the following command:
```
XB.networkDiscover()
```
several responses (one from each device) are received in the form:
```
2016-07-07 13:33:20.555 IN (addr: local ) Registry ’ND’ = ’FFFE0013A20040E44BA92000FFFE0100C105101E38’; [OK]
```

In this example case, the received data can be interpreted in the following way:
- _reserved_: `’FFFE’`
- high address: `’0013A200’`
- low address: `’40E44BA9’`
- node identifier: `’2000’`
- parent network address: `’FFFE’`
- device type: `’01’` (`’00’`: coordinator, `’01’`: router, `’02’`: end-point)
- reserved: `’00’`
- profile ID: `’C105’`
- manufacturer ID: `’101E’`
- RSSI of last hop: `’38’` = −0x38dBm = −56dBm. Note that this additional value is a consequence
of having set `’NO’` = `0x04`.


### findNeighbors()
Find Neighbors feature is very similar to the Network Discover feature as it produce the same kind of reply. The difference is the range of devices it can reach; only RF reachable devices will reply to
the Find Neighbors command.

It might be of interest therefore to know the neighbors of both local and remote XBee modules, as a remote device can have different neighbors then the locale.
`findNeighbors()` method is therefore requiring the high and slow addresses of the module to enquire.
`’LOCAL’` can be set for either high or low address to find neighbors of the local XBee module.

A possible example can be:
```
XB.findNeighbors(’0013a200’, ’40e44ba9’)
```
or
```
XB.findNeighbors(’’, ’LOCAL’)
```

Any response would be in the form:
```
2016-07-08 18:25:31.140 IN (addr: local ) Registry ’FN’ = ’FFFE0013A20040D4B3E72000FFFE0100C105101E48’; [OK]
```
which can be interpreted in the same way as the Network Discovery response.


### traceRoute()
Trace Routing is a feature recommended for testing setups only capable of providing route information from the local XBee module to a remote one, maybe not within RF range.

The command requests as input the high and low addresses of the module to route tracing.
It is not allowed to attempt Route Tracing for the local XBee. It is also not allowed to broadcast a
route tracing command.

After sending the following command:
```
XB.traceRoute()
```
one or several responses (one from each hop) are received in the form:
```
2016-07-08 18:39:06.104 IN (addr: 40e44b40) Route Info ’40e44b40’ to ’40d8789e’; receiver: 40d4b3e7
```

In this example, the route tracing request was from module `’40e44b40’` (local) to `’40d8789e’`.
The communication was sent from `’40e44b40’` (local) to the next hop, in this case `’40d4b3e7’`.

The next response would look like:
```
2016-07-08 18:39:06.208 IN (addr: 40d4b3e7) Route Info ’40e44b40’ to ’40d8789e’; receiver: 40d8789e
```
meaning that, for the same route tracing command (from `’40e44b40’` (local) to `’40d8789e’`), the communication is now between node `’40d4b3e7’` and the final node `’40d8789e’`.
In this example there was only one hop between the local XBee module and the target `’40d8789e’`, thus only 2 responses were received.


### linkQualityTest()
The DigiMesh API [RD1] features the capability of internally (between the Xbee modules) testing the quality link of 2 devices in RF range between themselves.

The test allows to set a number of bytes to exchange between the 2 devices and a number of iterations for repeating the exchange.
If the transfer is successful a report is given back providing quality link data.

The Link can be performed between any device to any other device, as long as the two are within RF range between each other.

Information about the source (high and low) address and destination (high and low) address is to be passed to the method.
It is also possible to define the number of bytes to exchange and the iterations. If these are not provided, the default values of 32 bytes and 200 iterations are used respectively.

A possible example can be:
```
XB.linkQualityTest(XB.params[’SH’], XB.params[’SL’], ’0013a200’, ’40e44ba9’)
```

The response is in the form:
```
2016-07-08 18:15:51.811 IN (addr: local ) explicit transmit data: hex’0013A20040D4B3E7002000C800C80017000A494C49’; [status: 0]
```

where the data can be interpreted as:
- high address: `’0013A200’`
- low address: `’40D4B3E7’`
- payload size: `’0020’` (= 32 bytes)
- iterations: `’00C8’` (= 200)
- number of successful iterations: `’00C8’`
- number of retries: `’0017’`
- result: `’00’` (`’00’`: success, `’03’`: invalid parameter)
- maximum number of MAC retries: `’0A’`
- maximum RSSI: `’49’` (= −73dBm)
- minimum RSSI: `’4C’` (= −76dBm)
- average RSSI: `’49’` (= −73dBm)


## Contribution
This code was based on a different implementation by @bzoss
