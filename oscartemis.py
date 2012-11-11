import socket
import sys
import struct
import math

import simpleOSC

globaloptions = None

shipId = 0
shipStats = {"shield": -1, "energy" : -1 ,"coordY" : -1, "coordX" : -1, "warp rate" : -1,"rotation rate" : -1, "impulse rate" : -1, "unknown" : -1, "unknown2" : -1, "rotation":-1, "frontshield" : -1, "rearshield" : -1, "weaponlock" : -1, "autobeams": -1, "speed": -1}

statMapHelm = {15 : ("energy", 'f'), 21: ("coordY", 'f'), 19: ("coordX", 'f'), 16: ("shield", 'h'), 14: ("warp rate", 'b'), 10:("rotation rate", 'f'), 9: ("impulse rate", 'f'),  23: ("unknown2", 'f'), 25: ("speed", 'f'), 24: ("rotation", 'f'), 28: ("frontshield",'f'), 30: ("rearshield", 'f'), 8: ("weaponlock", "i"), 13:("autobeams",'b')}

numLens = { 'f' : 4, 'h' : 2, 'i' : 4, 'b' : 1}


def decBitField(bitstr):
	valcount = 0
	outstr = ""
	for i in range (0,32):
		bit = bitstr & (1 << i)
		if(bit > 0):
			valcount += 1
			outstr += "1"
		else :
			outstr += "0"
	return (valcount, outstr)

def decodePacket(bitStr, message, statsMap):
	global shipStats
	valPtr = 0
	goodPacket = True
	tempResults = {}
	for i in range(32):
		if bitStr  & (1 << i) > 0:
			try:
				mappedStat = statsMap[i]
				bound = numLens[mappedStat[1]]
				tempResults[mappedStat[0]] = struct.unpack(mappedStat[1], message[valPtr : valPtr + bound])
			except:
				goodPacket = False

			valPtr += bound
	if goodPacket:
		for stat in tempResults:
			shipStats[stat] = tempResults[stat]
		st = str(shipStats)
		return st
	else:
		return None
	



def processPacket(message):
	global shipId
	#get rid of empty packets
	if len(message) == 0:
		return
	#convert packet to ints rather than a massive string.
	mess = [ord(p) for p in message]

	
	#these four chars are the message type
	messType = mess[16:20]
	#some sort of object update	
	if  messType ==  [0xf9,0x3d,0x80,0x80]:
		#next 4 bytes are bitfieldtype, <ship id,shipid> 0
		if mess[20:24] == [0,0,0,0]:
			#keep-alive packet
			return
		else:
			#seems to be a bitfield, 1 is playership? 2 and 4 also seen
			playerShip = mess[20]
			if playerShip == 0x01:
				sId = struct.unpack("h", message[21:23])
				if shipId == 0:
					shipId = sId[0]
					print "GOT SHIP ID:", shipId

				c = struct.unpack("i", message[24:28])[0]
				v = decBitField(c)
				a = decodePacket(c, message[36:],statMapHelm)
				#print a

				for stat in shipStats:
					simpleOSC.sendOSCMsg("/shipstate/" + stat, [shipStats[stat]])
	
	elif messType == [0x3c, 0x94, 0x7e, 0x07]:
		pass

	elif messType == [0xc4, 0xd2, 0x3f, 0xb8]:
		#this is most likely not the format but it gives
		#repeatable results
		#print mess[24:], len(mess[24:])
		vals = struct.unpack("iiiiiiiiiiib", message[24:])
		if vals[2] == 1:
			if vals[6] == shipId:
				print "WE GOT HIT!"
				simpleOSC.sendOSCMsg("/shiphit", [1])
			print "Damage from %i to %i" %(vals[5:7])


	elif messType == [0x5f, 0xc3, 0x72, 0xd6]:
		#print "NEW: ", mess[24:]
		pass

	elif messType == [0xfe, 0xc8, 0x54, 0xf7]:
		#print "global? " , mess[20:]
		if mess[20:24] == [0,0,0,0]:
			print "global? " , mess[20:]
			if mess[24] == 1:
				#get ship id
				ship = struct.unpack("i", message[28:32])[0]
				print "ship asplode: ", ship
				if ship == shipId:
					simpleOSC.sendOSCMsg("/shipdestroy",[1])
					print "KABOOM MOTHERFUCKER!"
	elif messType == [0x11, 0x67, 0xe6, 0x3d]:
		print "SIM START", mess[20:]
		simpleOSC.sendOSCMsg("/simstart", [1])
		shipId = 0




# LETS START THIS MESS

if len(sys.argv) < 3:
	print "Artemis to OSC bridge"
	print "Usage:"
	print "  oscartemis.py <artemisserverip> <oscserverip>"
	sys.exit(1)

serverip = sys.argv[1]
oscip = sys.argv[2]

print "connecting to ", serverip, ".."
#packet header string

splitStr = "\xef\xbe\xad\xde"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((serverip, 2010))

print "..connected"
#start the OSC client
print "starting osc client and connecting to", oscip, ".."
simpleOSC.initOSCClient(oscip, port=12000)
print "..done"



buff = ""
packets = []
workingPacket = ""
while(True):
	'''
	d = sock.recv(256)
	dat = dat + d
	packets = dat.split(splitStr)
	for p in packets:
		processPacket(p)
	dat = dat[-1]
	'''
	buff = sock.recv(256)
	#scan the buffer for the start string and length
	packets = []
	startPacket = -1
	pktIndex = 0
	while pktIndex < len(buff):
		if buff[pktIndex : pktIndex + 4] == splitStr:
			#PAY ATTENTION BOND
			pktIndex += 4
			if len(workingPacket) > 0:
				packets.append(workingPacket)
				workingPacket = ""
		else:
			workingPacket += buff[pktIndex]
			pktIndex += 1
	
	for p in packets:
		processPacket(p)

			
	
	

			

			






