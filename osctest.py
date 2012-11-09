import pcapy
import dpkt
import sys
import struct
import math

import simpleOSC

globaloptions = None
log = open("log.txt", "w")

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
	



def processPacket(message, num):
	global shipId
	if len(message) == 0:
		return
	mess = [ord(p) for p in message]

	#ok classify based mess[40:44] then length
	# old base was 26
	messType = mess[16:20]
		
	if  messType ==  [0xf9,0x3d,0x80,0x80]:
		#next 4 bytes are bitfieldtype, <ship id,shipid> 0
		if mess[20:24] == [0,0,0,0]:
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

				for stat in shipStats:
					simpleOSC.sendOSCMsg("/shipstate/" + stat, [shipStats[stat]])
	
	elif messType == [0x3c, 0x94, 0x7e, 0x07]:
		pass

	elif messType == [0xc4, 0xd2, 0x3f, 0xb8]:
		vals = struct.unpack("iiiiiiiiiii", message[24:])
		if vals[2] == 1:
			if vals[6] == shipId:
				print "WE GOT HIT!"
			print "Damage from %i to %i" %(vals[5:7])
		print "DAMAGE? ", vals 


	elif messType == [0x5f, 0xc3, 0x72, 0xd6]:
		#print "NEW: ", mess[24:]
		pass

	elif messType == [0xfe, 0xc8, 0x54, 0xf7]:
		#print "LULWUT: ", mess[24:]	
		pass


inte = -1

if len(sys.argv) < 2 :
	l = pcapy.findalldevs()
	print l
	exit()
else:
	inte = int(sys.argv[1])
 
# list all the network devices
l = pcapy.findalldevs()
max_bytes = 1024
promiscuous = False
read_timeout = 100 # in milliseconds

#pc = pcapy.open_offline("captures/fun.pcap")
pc = pcapy.open_live(l[inte], max_bytes, promiscuous, read_timeout)
pc.setfilter('tcp src port 2010') 

splitStr =  "".join([chr(0xef),chr(0xbe), chr(0xad), chr(0xde)])
pktCount = 0

simpleOSC.initOSCClient("192.168.0.3", port=12000)


# callback for received packets
def recv_pkts(hdr, data):
	  global pktCount  
	  packet = dpkt.ethernet.Ethernet(data)
	  
	  packets = packet.data.tcp.data.split(splitStr)
	  #packets = packet.data.split(splitStr)
	  for p in packets:
		  processPacket(p,pktCount)
		  pktCount += 1
 
packet_limit = -1 # infinite
pc.loop(packet_limit, recv_pkts) # capture packets
log.close()


