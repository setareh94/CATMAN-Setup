var SerialPort = require('/home/pi/CATMAN-Setup/Network_Configuration/node_modules/serialport');

//var port = new SerialPort('/dev/serial0', {
//	  baudRate: 9600
		
//});

const port = new SerialPort('/dev/serial0');
port.on('open',()=>{
	console.log('Port Opened');
});
//console.log("open");
