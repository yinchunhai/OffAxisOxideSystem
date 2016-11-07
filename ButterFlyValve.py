import serial
import binascii
import time
import re
import struct

# Create the MFC class
class ButterFlyValve:
	def __init__(self, portname):
		self.portname = portname
		self.openSerialPort()

	# Serial port commands
	def openSerialPort(self):
		self.serialport=serial.Serial(port=self.portname,
									baudrate=9600,
									bytesize=serial.SEVENBITS,
									parity=serial.PARITY_EVEN,
									stopbits=serial.STOPBITS_ONE,
									timeout=2, 
									xonxoff=False,
									rtscts=False, 
									writeTimeout=None,
									dsrdtr=False, 
									interCharTimeout=None)
		self.serialport.setDTR(False)
		print "Butterfly Valve serial port is open!"

	def closeSerialPort(self):
		self.serialport.close()
		print "Butterfly Valve serial port is closed!"
	
	#Control commands
	def closeValve(self):
		self.serialport.write(bytes('C:\r\n'))
		time.sleep(1.0/1000.0)
		response = self.serialport.read(256)
		if response == 'C:':
			print "ButterFly Valve is closed!"
			
	def openValve(self):
		self.serialport.write(bytes('O:\r\n'))
		time.sleep(1.0/1000.0)
		response = self.serialport.read(256)
		if response == 'O:':
			print "ButterFly Valve is open!"
			
oxide = ButterFlyValve('COM1')
oxide.closeValve()
time.sleep(5)
oxide.openValve()
oxide.closeSerialPort()


