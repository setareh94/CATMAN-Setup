/**
 * Created by lynmatten on 14.01.15.
 */


var XbeeHelper = require('./xbee-helper');

var ZigBeeHelper = new XbeeHelper.ZigBeeHelper(false, true);

/**
 * returns an object with parsed at commands
 */
console.log(ZigBeeHelper.getATCommand('AT+1=OK,2=0'));


/**
 * printing the frame in a efficient visual way
 */
var dataStr = "AT+1=OK";

var frame_obj = {
    type: 144,
    remote16: '1A000000000FF',
    remote64: '1AFF',
    receiveOptions: 0x01,
    data: ZigBeeHelper.StringToByteArray(dataStr)


};

console.log(ZigBeeHelper.printFrame(frame_obj));

console.log(ZigBeeHelper.getStringForDate(new Date()));