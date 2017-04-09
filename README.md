# CATMAN Software Component

### Concept
The generated algorithm has been designed in order to create a mesh network required for the communication of the XBee nodes. The figure below represents the current concept of message passing in order to develop the mesh network and coordinate the CubeSats data.

Digimesh allows for synchronization between sleeping nodes. This capability uses the method of message passing by defining different XBee nodes on the network as end nodes and routing the message around the mesh network toward them. 


![alt text](https://github.com/setareh94/CATMAN-Setup/blob/master/docs/concept.png "diagram")

### Initalization

We use [node-serialport]("https://github.com/EmergingTechnologyAdvisors/node-serialport") and node.js in order to initialize the networks for the xbee to discover each other 

```
node init_network.js
```

the above command should start the discovery of the nodes and send messages in order to send custom messages the following script will run the data in parallel along with python receiver script

```
node parallelRecieve.js
```

otherwise running 

```
python receiverScript.py
```
will initialize the sent messages that mentioned before.


### Testing


Testing is done with mocha test framework, chai assertion library, and sinon test framework. We set the environment variables ```XBEE_DEVICE``` and ```XBEE_BAUD```, then run 
```
npm test or mocha
``` 
For this to work, there must be at least one other XBee on the network to bounce messages off of. Node.js unit testing provides easier safeguarding criteria that we are looking for in order to make sure our CubeSat communication is stable. We write a unit test to make sure all the modules are working and dependencies are stubbed with providing fake dependencies. I have created a test-runner (mocha), assertion library (chai). The test-runner feeds fake data and different ports to assure the existence of the message flow throughout the network. Assertion library asserts for signals, array of existing nodes on the server and date of the last activity throughout the network. I have also used Spies, the unit testing interface provided with node.js which would help to get information on the function calls and force the code path with regards to passing variables. Overall all, the written testing functions provide the proof of stability of message passing with mesh network interface and stability of API callbacks.

### FAQ

GPS does not work? No Problem follow below
```
sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
```
Or config here
```
/etc/default/gpsd
```

Installing node-modules:
```
cp -r CATMAN-setup/node-modules /opt/nodejs/lib/
```

