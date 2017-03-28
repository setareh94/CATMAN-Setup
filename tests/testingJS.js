//var Xbee = require('digimesh');
var Xbee = require('/opt/nodejs/lib/node_modules/digimesh');
console.log('here')
var xbee = new Xbee({ device:'dev/serial0', baud: 9600 }, function() {
	    console.log('xbee is ready');
	   // xbee.discover_nodes(function(err, nodes) {
	//	        if (err) return console.err(err);
//
//		        console.log('%d nodes found:', nodes.length);
//		        console.dir(nodes);
//	    });
	});
