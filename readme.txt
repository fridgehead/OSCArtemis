---OSCArtemis

attempt to bridge Artemis ship stats to OSC for special effects etc

so far the protocol is half documented in the notes.txt file. The script rips updates from the network stream and sticks them in a dictionary



osctest.py forwards all tracked stats to an IP using OSC. This was tested with a processing sketch as the destination and found to be pretty decent at updating


Both scripts require pcapy and python 2.5 (as pcapy doesnt seem to work with 2.6+). The OSC test requires pyOSC and SimpleOSC


TODO:
added weapon hits to the stream
tidy!
