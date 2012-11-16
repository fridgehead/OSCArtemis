
import struct



class Decoder:

	def __init__(self, sntFile):
		self.shipId = 0
		self.shipStats = {"shield": -1, "energy" : -1 ,"coordY" : -1, "coordX" : -1, "warp rate" : -1,"rotation rate" : -1, "impulse rate" : -1, "unknown" : -1, "unknown2" : -1, "rotation":-1, "frontshield" : -1, "rearshield" : -1, "weaponlock" : -1, "autobeams": -1, "speed": -1}

		self.statMapHelm = {15 : ("energy", 'f'), 21: ("coordY", 'f'), 19: ("coordX", 'f'), 16: ("shield", 'h'), 14: ("warp rate", 'b'), 10:("rotation rate", 'f'), 9: ("impulse rate", 'f'),  23: ("unknown2", 'f'), 25: ("speed", 'f'), 24: ("rotation", 'f'), 28: ("frontshield",'f'), 30: ("rearshield", 'f'), 8: ("weaponlock", "i"), 13:("autobeams",'b')}

		self.numLens = { 'f' : 4, 'h' : 2, 'i' : 4, 'b' : 1}
		self.shipMap = self.loadShipData(sntFile) 

	def loadShipData(self, sntFile):
		maxX = 5
		maxY = 4
		maxZ = 9
		x,y,z = 0,0,0
		shipMap = {}

		namemap = ["Primary Beam", "Torpedo", "Tactical", "Maneuver", "Impulse", "Warp", "Front Shield", "Rear Shield"]
		print "loadint snt file.."
		f = open("artemis.snt", "r")

		for block in iter(lambda: f.read(32), ""):
			
			coords =  struct.unpack("fff", block[0:12])

			#print [ord(p) for p in block[12:] ], coords
			if ord(block[12]) < 254:
				print x,y,z, "=",namemap[ord(block[12])]
				key = "%i%i%i",(x,y,z)
				shipMap[key] = namemap[ord(block[12])]


			if z < maxZ:
				z += 1
			else:
				z = 0
				if y < maxY:
					y += 1
				else :
					y = 0
					x += 1
					x %= maxZ
		print "..done"
		return shipMap

			

	def decBitField(self, bitstr):
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

	def decodePacket(self, bitStr, message, statsMap):
		valPtr = 0
		goodPacket = True
		tempResults = {}
		bound = 0
		for i in range(32):
			if bitStr  & (1 << i) > 0:
				try:
					mappedStat = statsMap[i]
					bound = self.numLens[mappedStat[1]]
					tempResults[mappedStat[0]] = struct.unpack(mappedStat[1], message[valPtr : valPtr + bound])
				except:
					goodPacket = False

				valPtr += bound
		st = ""
		if goodPacket:
			for stat in tempResults:
				self.shipStats[stat] = tempResults[stat]
				st = str(self.shipStats)
			return st
		else:
			return None
		



	def processPacket(self, message):
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
					if self.shipId == 0:
						self.shipId = sId[0]
						print "GOT SHIP ID:", self.shipId

					c = struct.unpack("i", message[24:28])[0]

					v = self.decBitField(c)
					a = self.decodePacket(c, message[36:],self.statMapHelm)

		elif messType == [0xc4, 0xd2, 0x3f, 0xb8]:
			vals = None
			try:
				vals = struct.unpack("iiiiiiiiiii", message[24:])
				if vals[2] == 1:
					if vals[6] == self.shipId:
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
					if ship == self.shipId:

						print "KABOOM MOTHERFUCKER!"

		elif messType == [0x30, 0x3e, 0x5a, 0xcc]:
			print "oh?", mess[20:]
			pass
		elif messType == [0x3c,0x9f,0x7e,0x7]:
			print "engineering packet"

			if mess[21] == 255:
				pass
				#print "print damage crew moving"
			else :
				print mess[20:]
				for i in range(0, len(mess[21:]), 7):
					toDec = message[21 + i : 21 + i+7]

					if ord(toDec[0]) != 255:
						damage = struct.unpack("f", toDec[3:7])[0]
						print "Subsystem damage " ,"--" * 20
						x,y,z = [ord(p) for p in toDec[0:3]]
						print ".. at x:%i y:%i z:%i - damage now: %f" %(x,y,z, damage)
					else:
						break
				#print mess[20:]
		elif messType == [0x26, 0x12, 0x82, 0xf5]:
			pass
		elif messType == [0x11, 0x67, 0xe6, 0x3d]:
			print "SIM START", mess[20:]
			self.shipId = 0


		else:
			if messType == []:
				return
			print "UNKNOWN " ,"--" * 20
			print [hex(p) for p in messType]
			print mess


