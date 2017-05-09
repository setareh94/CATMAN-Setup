/**
 * Created by lynmatten on 14.01.15.
 */


var XbeeHelper = require('../../src/xbee-helper.js');


describe('xbee-helper class', function() {

    var ZigBeeHelper = new XbeeHelper.ZigBeeHelper();

    it('should create a valid object', function() {

        expect(ZigBeeHelper).toBeDefined();
        expect(ZigBeeHelper).not.toBeNull();
    });

    describe('API', function() {

        var ZigBeeHelper = null;

            beforeEach(function() {

                ZigBeeHelper = new XbeeHelper.ZigBeeHelper(false, true);

        });

        afterEach(function() {



        });

        describe('ByteToString() function', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.ByteToString).toBeDefined();

            });

            it('should correctly convert a byte array to a string', function() {

                var byte = [72,101,108,108,111,32,87,111,114,108,100,33]; /*Hello World!*/
                var string = "Hello World!";

                expect(ZigBeeHelper.ByteToString(byte)).toBe(string);


            });

            it("should remove all \r\n combinations while converting", function() {

                var data = [ 65, 84, 43, 76, 67, 75, 61, 79, 75, 13, 10 ] ;

                expect(ZigBeeHelper.ByteToString(data, true)).toBe("AT+LCK=OK");
            });

            it("should return '<< UNDEFINED >>' if parameter is undefined or null", function() {

                expect(ZigBeeHelper.ByteToString(undefined)).toBe("<< UNDEFINED >>");
                expect(ZigBeeHelper.ByteToString(null)).toBe("<< UNDEFINED >>");
            });

        });

        describe('StrinToByteArray() function', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.StringToByteArray).toBeDefined();

            });

            it('should correctly convert a string to a byte array', function() {

                var byte = [72,101,108,108,111,32,87,111,114,108,100,33]; /*Hello World!*/
                var string = "Hello World!";

                expect(ZigBeeHelper.StringToByteArray(string)).toEqual(byte);

            });

        });


        describe('printFrame() function', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.printFrame).toBeDefined();
            });

            it('should print a default message', function() {


                var testFrame = {
                    type: 'test'
                };

                var defaultMessage = "ERROR: " + ZigBeeHelper.getStringForDate(new Date()) +" !! Unknown frame type: test";

                expect(ZigBeeHelper.printFrame(testFrame)).toEqual(defaultMessage);

            });

            it('should return a valid message for Zigbee Remote At Command Request 0x17 with command MY', function() {

                var obj = {
                    type: 0x17, // xbee_api.constants.FRAME_TYPE.REMOTE_AT_COMMAND_REQUEST
                    id: 0x01, // optional, nextFrameId() is called per default
                    destination64: "0013a20040401122",
                    destination16: "fffe", // optional, "fffe" is default
                    remoteCommandOptions: 0x02, // optional, 0x02 is default
                    command: "MY",
                    commandParameter: [ 0x01 ] // Can either be string or byte array.
                };

                var result = 'OUT: '+ ZigBeeHelper.getStringForDate(new Date()) +' >> Send broadcast short Mac address request fffe for 0013a20040401122';

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });


            it('should return a valid message for Zigbee Remote Command Response 0x97 with command MY', function() {

                var obj = {
                    type: 0x97, // xbee_api.constants.FRAME_TYPE.REMOTE_COMMAND_RESPONSE
                    id: 0x01,
                    remote64: "0013a20040522baa",
                    remote16: "7d84",
                    command: "MY",
                    commandStatus: 0x00,
                    commandData: [ 0x40, 0x52, 0x2b, 0xaa ]
                };

                var result = 'IN: '+ ZigBeeHelper.getStringForDate(new Date()) +' << Received Short Mac Address 7d84 for 0013a20040522baa';

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });


            it('should return a valid message for Zigbee Receive Packet (AO=0) 0x90 ', function() {

                var obj = {
                    type: 0x90, // xbee_api.constants.FRAME_TYPE.ZIGBEE_RECEIVE_PACKET
                    remote64: "0013a20040522baa",
                    remote16: "7d84",
                    receiveOptions: 0x01,
                    data: [ 0x52, 0x78, 0x44, 0x61, 0x74, 0x61 ]
                };

                var result = 'IN: '+ ZigBeeHelper.getStringForDate(new Date()) +' << Receive Packet - Data from 7d84 / 0013a20040522baa: RxData';

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });


            it('should return a valid message for Zigbee Explicit RX (AO=1) 0x91 ', function() {

                var obj = {
                    type: 0x91, // xbee_api.constants.FRAME_TYPE.ZIGBEE_EXPLICIT_RX
                    remote64: "0013a20040522baa",
                    remote16: "7d84",
                    receiveOptions: 0x01,
                    data: [ 0x52, 0x78, 0x44, 0x61, 0x74, 0x61 ]
                };

                var result = 'IN: '+ ZigBeeHelper.getStringForDate(new Date()) +' << Explicit RX - Data from 7d84 / 0013a20040522baa receive options: 1: RxData';

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });


            it('should return a valid message for Zigbee Transmit Status 0x8B', function() {

                var obj = {
                    type: 0x8B, // xbee_api.constants.FRAME_TYPE.ZIGBEE_TRANSMIT_STATUS
                    id: 0x01,
                    remote16: "7d84",
                    transmitRetryCount: 0,
                    deliveryStatus: 0,
                    discoveryStatus: 1
                };

                var result = 'IN: '+ ZigBeeHelper.getStringForDate(new Date()) +' >> Transmit status for id: 1 --> remote16: 7d84 transmitRetryCount: 0 deliveryStatus: 0 discoveryStatus : 1' ;

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });


            it('should return a valid message for Zigbee Transmit Request 0x10', function() {

                var obj = {
                    type: 0x10, // xbee_api.constants.FRAME_TYPE.ZIGBEE_TRANSMIT_REQUEST
                    id: 0x01, // optional, nextFrameId() is called per default
                    destination64: "0013a200400a0127",
                    destination16: "fffe", // optional, "fffe" is default
                    broadcastRadius: 0x00, // optional, 0x00 is default
                    options: 0x00, // optional, 0x00 is default
                    data: "TxData0A" // Can either be string or byte array.
                };

                var result = 'OUT: '+ ZigBeeHelper.getStringForDate(new Date()) +' >> Transmit request for id: 1 --> destination16: fffe / 0013a200400a0127 broadcastRadius: 0 options: 0 data : TxData0A';

                expect(ZigBeeHelper.printFrame(obj)).toEqual(result);

            });



        });


        describe('getATCommand() function', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.getATCommand).toBeDefined();

            });



        });

        describe('getDebug() function', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.getDebug).toBeDefined();
            });
        });


        describe('setDebug() function', function() {

            beforeEach(function() {



                spyOn(ZigBeeHelper,"setDebug");

            });

            it('should be implemented', function() {

                expect(ZigBeeHelper.setDebug).toBeDefined();
            });

            it('should be called', function() {

                ZigBeeHelper.setDebug();

                expect(ZigBeeHelper.setDebug).toHaveBeenCalled();

            });

            it('should be called with a boolean value', function() {

                ZigBeeHelper.setDebug(true);
                /*TODO: Check the parameter tyoe*/
                expect(ZigBeeHelper.setDebug).toHaveBeenCalledWith(true);
            });

            it('should return false if parameter is not a boolean value', function() {

                /*TODO: Complete this test */
                //var ret = th.setDebug("BLA");

                //expect(ret).toBe(false);
            });


        });

        describe('getATCommand', function() {

            it('should be implemented', function() {

                expect(ZigBeeHelper.getATCommand).toBeDefined();
            });

            it('should return a valid JSON object with pared values', function() {

                var testStr = 'AT+1=OK';
                var testObj = {

                    commandString: testStr,
                    arrLength: 1,
                    commandArr: [
                        {
                            commandName: '1',
                            commandParam: 'OK'
                        }
                    ]

                };

                expect(ZigBeeHelper.getATCommand(testStr)).toEqual(testObj);


            });

            it('should return null for an invalid AT command', function() {

                expect(ZigBeeHelper.getATCommand('ThisIsNoValidATCommand')).toBe(null);
                expect(ZigBeeHelper.getATCommand("")).toBeNull();
                expect(ZigBeeHelper.getATCommand("AT+")).toBeNull();
            });

        });


    });

});