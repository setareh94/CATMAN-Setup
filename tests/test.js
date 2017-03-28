var digimesh = require('/opt/nodejs/lib/node_modules/digimesh');


	before(function(done) {
			    process.env.XBEE_DEVICE = process.env.XBEE_DEVICE || "/dev/serial0”;
			    process.env.XBEE_BAUD = process.env.XBEE_BAUD || 9600;
			    this.timeout(5000);


			    this.xbee = new digimesh({
				    	        device: process.env.XBEE_DEVICE,
				    	        baud: process.env.XBEE_BAUD,
				    	    }, done);
			});
