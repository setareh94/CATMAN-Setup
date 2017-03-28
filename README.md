# CATMAN Software Component

#### Concept
The generated algorithm has been designed in order to create a mesh network required for the communication of the XBee nodes. The figure below represents the current concept of message passing in order to develop the mesh network and coordinate the CubeSats data.

Digimesh allows for synchronization between sleeping nodes. This capability uses the method of message passing by defining different XBee nodes on the network as end nodes and routing the message around the mesh network toward them. 


![alt text](https://github.com/setareh94/CATMAN-Setup/blob/master/docs/concept.png "diagram")

#### Initalization

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


#### Testing


This repo contains all of the code requires to setup the Cube Sat network.
