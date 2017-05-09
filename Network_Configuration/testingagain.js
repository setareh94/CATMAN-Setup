//var Xbee = require('./digimesh');
var Xbee = require('./digimesh');

var xbee = new Xbee({ device: '/dev/serial0', baud:9600 }, function() {
    console.log('xbee is ready');
    // do stuff
});
