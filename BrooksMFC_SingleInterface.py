#!/usr/bin/env python

# Let's import stuff...
import wx
import serial
import numpy as np
import sys
import os
import binascii
import time
import re
import struct
from wx.lib import masked
from led import LED

# Create the MFC class
class MFC:
	mfcCount = 0
	
	def __init__(self, portname, gas):
		self.portname = portname
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

		self.serialport=serial.Serial(port=self.portname,baudrate=19200,bytesize=serial.EIGHTBITS, \
				parity=serial.PARITY_ODD,stopbits=serial.STOPBITS_ONE,timeout=0, xonxoff=False, \
				rtscts=False, writeTimeout=None, dsrdtr=False, interCharTimeout=None)
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
		preamble="FFFFFFFF"
		delimiter="82"
		retDelim = "86"
		address="8A5A0F462A"

		if debug: print "Sending (preamble & checksum not included):", delimiter, address, cmd, bytecount, data
		middle = self.hexToStr(delimiter+address+cmd+bytecount+data)
		csum=self.createChecksum(middle)

		#Is the serial port open?
		if(self.serialport.isOpen() == False): self.openSerialPort()
		if(self.serialport.isOpen() == True):
			#Flush stuff
			self.serialport.flushInput()
			self.serialport.flushOutput()

			#Write command
			self.serialport.write(self.hexToStr(preamble)+middle+csum)
			if debug: print "Wrote data to serial port"

			#Read response
			response=self.readMFC(retDelim, address, cmd)
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
                #Command specific information
                cmd = self.usiToHex(231)
                data = self.usiToHex(0)
                bytecount = self.usiToHex(len(data)/2)

                returnData = self.communicateMFC(cmd, bytecount, data)
                if len(returnData) == 1 and returnData!= "FAULT":
                	[valvestatus] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			if valvestatus == 0: return True
			else: return False
		else:
                        print returnData
			return False

        # Set valve override open
        def setValveOverrideOpen(self):
                #Command specific information
                cmd = self.usiToHex(231)
                data = self.usiToHex(1)
                bytecount = self.usiToHex(len(data)/2)

                returnData = self.communicateMFC(cmd, bytecount, data)
                if len(returnData) == 1 and returnData!= "FAULT":
                 	[valvestatus] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			if valvestatus == 1: return True
			else: return False
		else:
                        print returnData

        # Set valve override close
        def setValveOverrideClose(self):
                #Command specific information
                cmd = self.usiToHex(231)
                data = self.usiToHex(2)
                bytecount = self.usiToHex(len(data)/2)

                returnData = self.communicateMFC(cmd, bytecount, data)
                if len(returnData) == 1 and returnData!= "FAULT":
                  	[valvestatus] = struct.unpack('>I', "000000".decode("hex")+returnData[0])
			if valvestatus == 2: return True
			else: return False
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

# Create a new frame class, derived from the wxPython Frame.
class MyFrame(wx.Frame):

    def __init__(self, parent, id, title, size):
        # First, call the base class' __init__ method to create the frame
        wx.Frame.__init__(self, parent, id, title, size=(600,600))

	# Test MFC
	self.mfc1 = MFC('COM4', 'Ar')

	# Main panel
	topPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

	# Status items
	flowRateLabel = wx.StaticText(topPanel, -1, "Flow Rate:")
	self.flowRateCtrl = wx.TextCtrl(topPanel, -1, "", size=(120, 22), style=wx.TE_READONLY)
	getSetpointLabel = wx.StaticText(topPanel, -1, "Setpoint:")
	self.getSetpointPercentageCtrl = wx.TextCtrl(topPanel, -1, "", size=(120, 22), style=wx.TE_READONLY)
	self.getSetpointUnitCtrl = wx.TextCtrl(topPanel, -1, "", size=(120, 22), style=wx.TE_READONLY)
	comPortStatusLabel = wx.StaticText(topPanel, -1, "COM Status:")
	self.comPortStatusLED = LED(topPanel)
	valveStatusLabel = wx.StaticText(topPanel, -1, "Valve Status:")
	self.valveStatusLED = LED(topPanel)

	# Timers
	self.statusTimer = wx.Timer(self)
        self.timerToggleBtn = wx.Button(topPanel, wx.ID_ANY, "Toggle timer")
	statusTimerLabel = wx.StaticText(topPanel, -1, "Timer Status:")
	self.statusTimerLED = LED(topPanel)

	self.uiTimer = wx.Timer(self)
	self.uiTimer.Start(100)

	# Control items
	self.closeSerialBut = wx.Button(topPanel, wx.ID_ANY, 'Close serialport')
	self.openSerialBut = wx.Button(topPanel, wx.ID_ANY, 'Open serialport')
	self.setSetpointBut = wx.Button(topPanel, wx.ID_ANY, 'SET')
	self.setSetpointCtrl = masked.NumCtrl(topPanel, -1, integerWidth=3, fractionWidth=2, min=0.00, max=100.00)
	valveOverrideLabel = wx.StaticText(topPanel, wx.ID_ANY, 'Valve Override:')
	self.setValveOverrideOffBut = wx.Button(topPanel, wx.ID_ANY, 'OFF')
	self.setValveOverrideOpenBut = wx.Button(topPanel, wx.ID_ANY, 'OPEN')
	self.setValveOverrideCloseBut = wx.Button(topPanel, wx.ID_ANY, 'CLOSE')

	# Layout
	vbox = wx.BoxSizer(wx.VERTICAL)

	hbox1 = wx.BoxSizer(wx.HORIZONTAL)
	hbox1.Add(flowRateLabel, flag=wx.RIGHT, border=8)
	hbox1.Add(self.flowRateCtrl, proportion=1)

	vbox.Add(hbox1, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox6 = wx.BoxSizer(wx.HORIZONTAL)
	hbox6.Add(getSetpointLabel, flag=wx.RIGHT, border=8)
	hbox6.Add(self.getSetpointPercentageCtrl, proportion=1)
	hbox6.Add(self.getSetpointUnitCtrl, proportion=1)

	vbox.Add(hbox6, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox2 = wx.BoxSizer(wx.HORIZONTAL)
	hbox2.Add(comPortStatusLabel)
	hbox2.Add(self.comPortStatusLED)

	vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox3 = wx.BoxSizer(wx.HORIZONTAL)
	hbox3.Add(valveStatusLabel)
	hbox3.Add(self.valveStatusLED)

	vbox.Add(hbox3, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox4 = wx.BoxSizer(wx.HORIZONTAL)
	hbox4.Add(statusTimerLabel)
	hbox4.Add(self.statusTimerLED)

	vbox.Add(hbox4, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox5 = wx.BoxSizer(wx.HORIZONTAL | wx.ALIGN_LEFT)
	hbox5.Add(valveOverrideLabel)
	hbox5.Add(self.setValveOverrideOffBut)
	hbox5.Add((10,-1))
	hbox5.Add(self.setValveOverrideOpenBut)
	hbox5.Add((10,-1))
	hbox5.Add(self.setValveOverrideCloseBut)

	vbox.Add(hbox5, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox7 = wx.BoxSizer(wx.HORIZONTAL | wx.ALIGN_LEFT)
	hbox7.Add(self.timerToggleBtn)
	hbox7.Add((10,-1))
	hbox7.Add(self.closeSerialBut)
	hbox7.Add((10,-1))
	hbox7.Add(self.openSerialBut)

	vbox.Add(hbox7, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	hbox8 = wx.BoxSizer(wx.HORIZONTAL)
	hbox8.Add(self.setSetpointCtrl)
	hbox8.Add((10,-1))
	hbox8.Add(self.setSetpointBut)

	vbox.Add(hbox8, flag=wx.LEFT | wx.TOP, border=10)
	vbox.Add((-1, 10))

	topPanel.SetSizer(vbox)


	# Bindings
	self.Bind(wx.EVT_BUTTON, self.OnOpenSerialPort, self.openSerialBut)
        self.Bind(wx.EVT_BUTTON, self.OnCloseSerialPort, self.closeSerialBut)
	self.Bind(wx.EVT_BUTTON, self.OnSetSetpoint, self.setSetpointBut)
	self.Bind(wx.EVT_BUTTON, self.OnTimerToggle, self.timerToggleBtn)
	self.Bind(wx.EVT_TIMER, self.OnUIUpdate, self.uiTimer)
	self.Bind(wx.EVT_TIMER, self.OnStatusUpdate, self.statusTimer)
	self.Bind(wx.EVT_BUTTON, self.OnSetValveOverrideOff, self.setValveOverrideOffBut)
	self.Bind(wx.EVT_BUTTON, self.OnSetValveOverrideOpen, self.setValveOverrideOpenBut)
	self.Bind(wx.EVT_BUTTON, self.OnSetValveOverrideClose, self.setValveOverrideCloseBut)

	self.OnTimerToggle(wx.EVT_TIMER)
	self.OnSetValveOverrideClose(wx.EVT_BUTTON)

    # Open serial port
    def OnOpenSerialPort(self, event):
	self.mfc1.openSerialPort()

    # Close serial port
    def OnCloseSerialPort(self, event):
	self.mfc1.closeSerialPort()

    # Set Setpoint
    def OnSetSetpoint(self, event):
    	setpoint = self.setSetpointCtrl.GetValue()
	print setpoint
        self.mfc1.setFlowSetPointPercentage(setpoint)

    # Toggle timer
    def OnTimerToggle(self, event):        
        if self.statusTimer.IsRunning():
            self.statusTimer.Stop()
	    self.statusTimerLED.SetState(0)
        else:
            self.statusTimer.Start(2000)
	    self.statusTimerLED.SetState(2)

    # Update status timer
    def OnStatusUpdate(self, event):
	self.flowRateCtrl.SetValue(self.mfc1.readPrimaryValue())	
	sp=self.mfc1.readFlowSetPoint()
	self.getSetpointUnitCtrl.SetValue(sp['ml/min']+' ml/min')
	self.getSetpointPercentageCtrl.SetValue(sp['%']+' %')

    # Update uiTimer
    def OnUIUpdate(self, event):
	    if(self.mfc1.serialport.isOpen()): self.comPortStatusLED.SetState(2)
	    else: self.comPortStatusLED.SetState(0)

    # Set valve override off
    def OnSetValveOverrideOff(self, event):
	if self.mfc1.setValveOverrideOff(): 
		self.setValveOverrideCloseBut.SetBackgroundColour('red')
		self.setValveOverrideOpenBut.SetBackgroundColour('red')
		self.setValveOverrideOffBut.SetBackgroundColour('lightgreen')

    # Set valve override open
    def OnSetValveOverrideOpen(self, event):
	if self.mfc1.setValveOverrideOpen():
		self.setValveOverrideCloseBut.SetBackgroundColour('red')
		self.setValveOverrideOpenBut.SetBackgroundColour('lightgreen')
		self.setValveOverrideOffBut.SetBackgroundColour('red')

    # Set valve override close
    def OnSetValveOverrideClose(self, event):
	if self.mfc1.setValveOverrideClose():
		self.setValveOverrideCloseBut.SetBackgroundColour('lightgreen')
		self.setValveOverrideOpenBut.SetBackgroundColour('red')
		self.setValveOverrideOffBut.SetBackgroundColour('red')


# Every wxWidgets application must have a class derived from wx.App
class MyApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        # Create an instance of our customized Frame class
        frame = MyFrame(None, -1, "Brooks MFC", size=(400,400))
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        # Return a success flag
        return True

app = MyApp(0)     # Create an instance of the application class
app.MainLoop()     # Tell it to start processing events



