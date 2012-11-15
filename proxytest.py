import sys
import struct
import math
import time
import socket

globaloptions = None
log = open("log.txt", "w")

shipId = 0
shipStats = {"shield": -1, "energy" : -1 ,"coordY" : -1, "coordX" : -1, "warp rate" : -1,"rotation rate" : -1, "impulse rate" : -1, "unknown" : -1, "unknown2" : -1, "rotation":-1, "frontshield" : -1, "rearshield" : -1, "weaponlock" : -1, "autobeams": -1, "speed": -1}

statMapHelm = {15 : ("energy", 'f'), 21: ("coordY", 'f'), 19: ("coordX", 'f'), 16: ("shield", 'h'), 14: ("warp rate", 'b'), 10:("rotation rate", 'f'), 9: ("impulse rate", 'f'),  23: ("unknown2", 'f'), 25: ("speed", 'f'), 24: ("rotation", 'f'), 28: ("frontshield",'f'), 30: ("rearshield", 'f'), 8: ("weaponlock", "i"), 13:("autobeams",'b')}

numLens = { 'f' : 4, 'h' : 2, 'i' : 4, 'b' : 1}

catalog = {}

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
	bound = 0
	for i in range(32):
		if bitStr  & (1 << i) > 0:
			try:
				mappedStat = statsMap[i]
				bound = numLens[mappedStat[1]]
				tempResults[mappedStat[0]] = struct.unpack(mappedStat[1], message[valPtr : valPtr + bound])
			except:
				goodPacket = False

			valPtr += bound
	st = ""
	if goodPacket:
		for stat in tempResults:
			shipStats[stat] = tempResults[stat]
			st = str(shipStats)
		return st
	else:
		return None
	



def processPacket(message):
	global shipId
	if len(message) == 0:
		return
	mess = [ord(p) for p in message]

	messType = mess[16:20]
		
	if  messType ==  [0xf9,0x3d,0x80,0x80]:
		#next 4 bytes are bitfieldtype, <ship id,shipid> 0
		if mess[20:24] == [0,0,0,0] or len(mess[24:]) == 0:
			return
		else:
			playerShip = mess[20]
			if playerShip == 0x01:
				sId = struct.unpack("h", message[21:23])
				if shipId == 0:
					shipId = sId[0]
					print "GOT SHIP ID:", shipId

				c = struct.unpack("i", message[24:28])[0]

				v = decBitField(c)
				a = decodePacket(c, message[36:],statMapHelm)

	elif messType == [0xc4, 0xd2, 0x3f, 0xb8]:
		vals = None
		try:
			vals = struct.unpack("iiiiiiiiiii", message[24:])
			if vals[2] == 1:
				if vals[6] == shipId:
					print "WE GOT HIT!"
					pass
			print "Damage from %i to %i" %(vals[5:7])

			print "DAMAGE? ", vals 


		except struct.error:
			print "unpack error"
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

					print "KABOOM MOTHERFUCKER!"

	elif messType == [0x30, 0x3e, 0x5a, 0xcc]:
		print "oh?", mess[20:]
		pass
	elif messType == [0x3c,0x94,0x7e,0x7]:
		#print "eng " ,"--" * 20
	#	print [hex(p) for p in messType]
	#	print mess
		c = struct.unpack("i", message[20:24])[0]
		v = decBitField(c)
		print v[1]
	elif messType == [0x26, 0x12, 0x82, 0xf5]:
		pass
	elif messType == [0x11, 0x67, 0xe6, 0x3d]:
		print "SIM START", mess[20:]
		shipId = 0


	else:
		if messType == []:
			return
		print "UNKNOWN " ,"--" * 20
		print [hex(p) for p in messType]
		print mess

if len(sys.argv) < 2:
	print "Artemis to OSC bridge"
	print "Usage:"
	print "  oscartemis.py <artemisserverip> <oscserverip>"
	sys.exit(1)

serverip = sys.argv[1]

buff = ""

packets = []
workingPacket = ""
pktCount = 0
selectionPacketSent = False

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("127.0.0.1", 2011))
serversocket.listen(1)
print "Waiting for connection..."
serverSock = None

while True:
	(serverSock, addr) = serversocket.accept()
	print "got connection from ", addr
	break


print "now connecting to ", serverip, ".."

#packet header string

splitStr = "\xef\xbe\xad\xde"

print "..connected"
print "conecting to artemis server.."
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((serverip, 2010))




while(True):
	#get data from client
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
		pktCount += 1
		#write out the packet to the outgoing conn
		serverSock.send(p)

	sock.send(serverSock.recv(100))

	
		
	
	

			

			






