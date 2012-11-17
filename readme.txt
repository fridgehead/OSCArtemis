==== ArtemisProxy.py ====

A man in the middle proxy for the Artemis bridge simulator. Pipes events from the game to an OSC server to allow special effects to be triggered or for new visual displays to be added


Requirements:
ArtemisProxy.py requires the following libraries
>simpleOSC
>pyOSC

the other scripts are for testing, they can be ignored

Usage:
ArtemisProxy : proxy between Artemis clients and server, forwards certain events to OSC server
       [-h] --serverip SERVERIP --listenip LISTENIP
       [--oscserverip OSCSERVERIP] --sntfile SNTFILE

optional arguments:
  -h, --help            show this help message and exit
  --serverip SERVERIP   Artemis server IP
  --listenip LISTENIP   ip to listen for clients on
  --oscserverip OSCSERVERIP
                        OSC server IP
  --sntfile SNTFILE     snt file of ship being used


the sntfile is the .snt file for ths ship being used in the sim. Theyre found in the "dat" folder of the artemis installation. Its used to map ship damage to subsytem names. To figure out which one to use check "Vesseldata.xml"

oscserverip is optional, leave it out and the tool will function but not do anything useful :) you can specify the port by using the form ip:port (eg 127.0.0.1:12000)

Start this tool on a client machine with serverip set to the Artemis server ip and listenip set to the local IP of the machine. 
Then start the Artemis client and connect to the local IP, it should connect normally and the tool should start showing data passing through.

Make sure that the client is set to use the "engineering" station or you dont get the full set of stats out of the tool


When running the tool sends the following osc messages prefixed with "/shipstate/":
"shield"
"energy"
"coordY"
"coordX"
"warp rate"
"rotation rate"
"impulse rate"
"rotation"
"frontshield"
"rearshield"
"weaponlock"
"autobeams"
"speed"

values are a mixture of integers and floats, check the typetag when decoding for more info

The following are sent when events happen
"/shiphit"
"/shipdestroy"
"/simstart"

When ever ship subsystems are damaged (and the proxy is connected to an engineer station) the following event is generated:

"/subdamage"
This has 4 values associated with it
[0] Subsystem name eg: Warp
[1] Subsystem ID number eg: 221
[2] Total number of this subsystem types on this ship eg: 4
[3] Current damage level (0.0 - 1.0) eg: 0.0

the subsystem ID is actually its XYZ coordinate in the ships engineering view, but its unique sp makes for a good ID number 
The engineering stations subsystem damage display is actually calculate from how many subsystems are damaged. so 50% means 2 out of 4 nodes are damaged.

I havent decoded the weapons data yet

So far this has been confirmed as working with Processing sketches (using oscP5 library).
