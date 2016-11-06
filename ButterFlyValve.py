import serial
import binascii
import time
import re
import struct

serialport=serial.Serial(port='COM1',
							baudrate=9600,
							bytesize=serial.SEVENBITS,
							parity=serial.PARITY_EVEN,
							stopbits=serial.STOPBITS_ONE,
							timeout=0, 
							xonxoff=False,
							rtscts=False, 
							writeTimeout=None,
							dsrdtr=False, 
							interCharTimeout=None)
serialport.setDTR(False)

serialport.write(bytes('C:\r\n'))
time.sleep(2)
serialport.write(bytes('O:\r\n'))
br = serialport.read(256)
print br

