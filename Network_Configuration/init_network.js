'use strict';
var Xbee = require('./digimesh');

var xbee = new Xbee({ device: '/dev/serial0', baud: 9600 }, function() {
	    console.log('xbee is ready');

	    console.log('getting node identifier...');
	    xbee.get_ni_string(function(err, data) {
		            if (err) return console.err(err);
		            console.log("my NI is '" + data.ni + "'");

		            console.log('scanning for nodes on the network...');
		            xbee.discover_nodes(function(err, nodes) {
				                if (err) return console.err(err);
				                console.log('%d nodes found:', nodes.length);
				                console.dir(nodes);

				                if (nodes.length) {
							                console.log("saying 'hello' to node %s...", nodes[0].addr);
							                xbee.send_message({
										                    data: new Buffer("hello"),
										                    addr: nodes[0].addr,
										                    broadcast: false,
										                },
										                function(err, data) {
													                    if (err) return console.error(err);
													                    console.log('delivery status: %s',
																                            xbee.DELIVERY_STATUS_STRINGS[data.status]);
													                    console.dir(data);
													                    console.log('goodbye');
													                    process.exit(0);
													                });
							            }
				            });
		        });
});

xbee.on('error', function(err) {
	    console.error(err);
	    process.exit(1);
});

xbee.on('message_received', function(data) {
	    console.log('received a message!');
	    console.dir(data);
});
