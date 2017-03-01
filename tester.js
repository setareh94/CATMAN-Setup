var SerialPort = require('/opt/nodejs/lib/node_modules/serialport')
var sp = new SerialPort('/dev/serial0', {
	      baudrate: 9600
}, false);

console.log("Starting up serial host...");

var message = "Num: ";
var counter = 1000000;

sp.open(function(err) {
	    if (err) {
		            console.log("Port open error: ", err);
		        }
	    else {
		            console.log("Port opened!");
		        }
});

function write()
{

	        if (sp.isOpen())  {
			            message= counter.toString();
			            counter+=1;

			            console.log("Writing serial data: " + message);
			            sp.write(message, function(err, res)
					                {
								                    if (err)
									                    {
												                                console.log(err);
												                        }
								                    setTimeout(write, 50);
								            });
			        }
	        else {
			            setTimeout(write, 50);
			        }
}

setTimeout(write, 10); //wait 10 ms for everything to initialize correctly
