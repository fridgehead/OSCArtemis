---OSCArtemis

attempt to bridge Artemis ship stats to OSC for special effects etc

Requirements:
oscartemis.py requires the following libraries
>simpleOSC
>pyOSC

the other scripts are for testing, they can be ignored

Usage:

python oscartemis.py <artemis server ip> <OSC Server IP>

The tool sends the following osc messages prefixed with "/shipstate/":
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

values are a mixture of integers and floats.

the following are sent when events happen

"/shiphit"
"/shipdestroy"
"/simstart"


So far this has been confirmed as working with Processing sketches (using oscP5 library).
