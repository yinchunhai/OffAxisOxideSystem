import serial
import binascii
import time
import re
import struct

# Create the MFC class
class MFC:
	mfcCount = 0
	def __init__(self, portname, address, gas):
		self.portname = portname
		self.address = address
		self.gas = gas

		MFC.mfcCount += 1
		MFC.flowRateDict = dict()
		tmp = {'17':'l/min', '19':'m3/h', '24':'l/s', '28':'m3/s', '57':'%', '131':'m3/min', '138':'l/h', '170':'ml/s', '171':'ml/min', '172':'ml/h'}
		for item in tmp:
			MFC.flowRateDict[item] = tmp[item]
			MFC.flowRateDict[tmp[item]] = item
		self.openSerialPort()

	# Takes normal ASCII string and returns packed ASCII chars
	def packData(self, s):
        	packedData = ""
	        for c in s:
	                bits = bin(ord(c))[2:]
			bits = '00000000'[len(bits):] + bits
                	packedBits = bits[2:8]
			packedData += packedBits
	        packedData = hex(int(packedData,2))
        	return packedData[2:].decode("hex")

	# Takes packed ASCII string returns ASCII string
	def unpackData(self, s):
		unpackedData = ""
		unpackedBits = ""
		for c in s:
			bits = bin(ord(c))[2:]
        	        bits = '00000000'[len(bits):] + bits
			unpackedBits += bits
		splits=[unpackedBits[x:x+6] for x in range(0,len(unpackedBits),6)]
		splits=['0' + str(int(s[0]) ^ 1) + s for s in splits]
		for s in splits:
			unpackedData += chr(int(s,2))
		return unpackedData

	# Convert ASCII string to 2-char hex sequence
	def strToHex(self, s):
		return "".join("{0:02x}".format(ord(c)) for c in s)

	# Convert 2-char hex sequence to ASCII string
	def hexToStr(self, h):
		return binascii.unhexlify(h)

	# Convert unsigned integer to  hex sequence
	def usiToHex(self, i):
		return self.strToHex(struct.pack('>I', i)[-1:])

	# Convert IEEE 754 32bit float to hex sequence
	def ieee754ToHex(self, f):
		return self.strToHex(struct.pack('>f', f))

	# Create checksum of ASCII string
	def createChecksum(self, s):
		csum=0
		for c in s:
			csum ^= ord(c)
		return chr(csum)

	# Open serial port
	def openSerialPort(self):
		self.serialport=serial.Serial(port=self.portname,
									baudrate=19200,
									bytesize=serial.EIGHTBITS,
									parity=serial.PARITY_ODD,
									stopbits=serial.STOPBITS_ONE,
									timeout=0, 
									xonxoff=False,
									rtscts=False, 
									writeTimeout=None,
									dsrdtr=False, 
									interCharTimeout=None)
		self.serialport.setDTR(False)

	# Close serial port
	def closeSerialPort(self):
		self.serialport.close()

	# Read response until the checksum is found and datalength matches
	def readMFC(self, retDelim, address, cmd):
		i=0
		read=""
		pattern = re.compile('^(ff){2,6}('+retDelim+')('+address+')('+cmd+')([0-9A-Fa-f]{2})([0-9A-Fa-f]{4})([0-9A-Fa-f]*)([0-9A-Fa-f]{2})$', re.IGNORECASE)
			
		for i in range(0, 100, 1):
			time.sleep(1.0/1000.0)
			read+=self.strToHex(self.serialport.read())
			if(pattern.match(read)):
				[results] = pattern.findall(read)
				if(len(results) == 8 and len(results[6]) > 1 and len(results[6]) % 2 == 0): #Check that results has 8 entries, received data is > 1 and has even characters
					#results[0]:pream, [1]:delim, [2]:addr, [3]:command, [4]:bytec, [5]:status, [6]:rdata, [7]:checksum
					csumString = results[1] + results[2] + results[3] + results[4] + results[5] + results[6]
					dataLength = len(results[5]+results[6])/2
					[byteCount] = struct.unpack('>I', self.hexToStr("000000"+results[4]))
					csum=self.createChecksum(self.hexToStr(csumString))
					if(dataLength == byteCount and self.strToHex(csum) == results[7]):
						return results[6] # we do nothing with the status!
						break
				if(i==99): 
					return "FAULT"
					break

	# Generic communication with MFC, takes arguments in hex string format, ie "Hello World" would be 48656C6C6F20576F726C64, returns ASCII formatted string
	def communicateMFC(self, cmd, bytecount, data):
		#Debugging purposes
		debug = False

		#General information
		preamble = "FFFFFFFF"
		delimiter= "82" #master to slave
		retDelim = "86" #slave to master
		address  = self.address
		
		if debug: print "Sending (preamble & checksum not included):", delimiter, address, cmd, bytecount, data
		middle = self.hexToStr(delimiter+address+cmd+bytecount+data)
		csum=self.createChecksum(middle)
		
		print 'middle is ', middle, 'csum is', csum
		
		#Is the serial port open?
		if(self.serialport.isOpen() == False): self.openSerialPort()
		if(self.serialport.isOpen() == True):
			#Flush stuff
			self.serialport.flushInput()
			self.serialport.flushOutput()

			#Write command
			self.serialport.write(self.hexToStr(preamble)+middle+csum)
			if debug: print "Write data to serial port"

			#Read response
			response=self.readMFC(retDelim, address, cmd)
			print response
			if debug: print "Data received:", response, len(response)/2, "characters"
			return self.hexToStr(response)
		else:
			return "FAULT"

	# Read primary value MFC and extract flow unit and rate
	def readPrimaryValue(self):
		#Command specific information
		cmd = self.usiToHex(1)
		data = ""
		bytecount = self.usiToHex(len(data))

		returnData = self.communicateMFC(cmd, bytecount, data)

		#Parse return data
		if(returnData != 0 and len(returnData) == 5 and returnData!= "FAULT"):
			[flowunit] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			[flowrate] = struct.unpack('>f', returnData[1:])
			if flowrate < 0.1: flowrate = 0.0
			return '{0:03.2f}'.format(flowrate) + " " + MFC.flowRateDict[str(flowunit)]
		else:
			return "FAULT"

	# Read serialnumber MFC
	def readSerialNumber(self):
		#Command specific information
		cmd = self.usiToHex(131)
		data = ""
		bytecount = self.usiToHex(len(data))

		returnData = self.communicateMFC(cmd, bytecount, data)

		if len(returnData) == 24 and returnData!= "FAULT":
			return self.unpackData(returnData)
		else:
			return "FAULT"

	# Read gas1 type MFC
	def readGasType():
		#Command specific information
		cmd = self.usiToHex(150)
		data = self.usiToHex(1)
		bytecount = self.usiToHex(1)

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) > 0 and returnData!= "FAULT": print len(returnData), " - ", struct.unpack('>B', returnData[0]), " - ", returnData[1:].rstrip("\0")

	# Read Full Scale Gas Flow MFC 
	def readFSGF():
		#Command specific information
		cmd = self.usiToHex(152)
		bytecount = self.usiToHex(1)
		data = self.usiToHex(1)

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) > 0 and returnData!= "FAULT": print len(returnData), " - ", struct.unpack('>B', returnData[0]), " - ", struct.unpack('>f', returnData[1:])

	# Set flow unit
	def setFlowUnit(self, unit):
		#Command specific information
		cmd = self.usiToHex(196)
		data = self.usiToHex(0)+self.usiToHex(unit)
		bytecount = self.usiToHex(len(data)/2)

		returnData = self.communicateMFC(cmd, bytecount, data)
		if(len(returnData) == 2 and returnData != "FAULT"):
			if(self.usiToHex(0) == self.strToHex(returnData[0]) and self.usiToHex(unit) == self.strToHex(returnData[1])): return True
			else: return False

	# Read flow setpoint
	def readFlowSetPoint(self):
		#Command specific information
		cmd = self.usiToHex(235)
		bytecount = self.usiToHex(0)
		data = ""

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) == 10 and returnData!= "FAULT": 
			[flowUnitPerc] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			[flowRatePerc] = struct.unpack('>f', returnData[1:5])
			[flowUnit] = struct.unpack('>I', "000000".decode("hex")+returnData[5])
			[flowRate] = struct.unpack('>f', returnData[6:])
			return {MFC.flowRateDict[str(flowUnitPerc)]:'{0:03.2f}'.format(flowRatePerc), MFC.flowRateDict[str(flowUnit)]:'{0:03.2f}'.format(flowRate)}

	# Set flow setpoint
	def setFlowSetPointPercentage(self, setpoint):
		#Command specific information
		cmd = self.usiToHex(236)
		data = self.usiToHex(57) + self.ieee754ToHex(setpoint)
		bytecount = self.usiToHex(len(data)/2)
		
		print cmd, data, bytecount

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) == 10 and returnData!= "FAULT": 
			[flowUnitPerc] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			[flowRatePerc] = struct.unpack('>f', returnData[1:5])
			[flowUnit] = struct.unpack('>I', "000000".decode("hex")+returnData[5])
			[flowRate] = struct.unpack('>f', returnData[6:])
			print '{0:03.2f}'.format(flowRatePerc) + " " + MFC.flowRateDict[str(flowUnitPerc)]
			print '{0:03.2f}'.format(flowRate) + " " + MFC.flowRateDict[str(flowUnit)]
		else: 
			print returnData

    # Set valve override off (0 OFF, 1 OPEN, 2 CLOSE, 3 MANUAL readonly)
	def setValveOverrideOff(self):
		cmd = self.usiToHex(231)
		data = self.usiToHex(0)
		bytecount = self.usiToHex(len(data)/2)
		
		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) == 1 and returnData!= "FAULT":
			print 'Set valve to', struct.unpack('>I', "000000".decode("hex")+returnData[0])
		else:
			print returnData

	# Set valve override open
	def setValveOverrideOpen(self):
		cmd = self.usiToHex(231)
		data = self.usiToHex(1)
		bytecount = self.usiToHex(len(data)/2)

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) == 1 and returnData!= "FAULT":
			print 'Set valve to', struct.unpack('>I', "000000".decode("hex")+returnData[0])
		else:
			print returnData

	# Set valve override close
	def setValveOverrideClose(self):
		cmd = self.usiToHex(231)
		data = self.usiToHex(2)
		bytecount = self.usiToHex(len(data)/2)
		
		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) == 1 and returnData!= "FAULT":
			print 'Set valve to', struct.unpack('>I', "000000".decode("hex")+returnData[0])
		else:
			print returnData

	# Read Valve Control Value 
	def readValveControlValue(self):
		#Command specific information
		cmd = self.usiToHex(237)
		data = "" 
		bytecount = self.usiToHex(len(data)/2)

		returnData = self.communicateMFC(cmd, bytecount, data)
		if len(returnData) > 0 and returnData!= "FAULT": 
			print returnData
			print struct.unpack('>I', "000000".decode("hex")+returnData[0])