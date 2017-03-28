var SerialPort = require('/opt/nodejs/lib/node_modules/serialport');
var port = new SerialPort('/dev/serial0', {
	  baudRate: 9600
		
});

console.log("open");
