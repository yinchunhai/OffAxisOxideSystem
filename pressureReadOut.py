from Tkinter import *
from decimal import Decimal
import numpy as np
import tkMessageBox
import serial 
import thread
import time
from perpetualTimer import perpetualTimer

class PressureReadOut():
	def __init__(self, portname):
		self.portname = portname
		self.openSerialPort()
		
	def openSerialPort(self):
		self.ser = serial.Serial(port=self.portname,
								baudrate = 57600,
								timeout = 100)
		self.ser.setDTR(False)
	
	def closeSerialPort(self):
		self.ser.close()
		
	def readPresure(self):
		self.ser.write(b'ADC0;')
		self.reading = self.ser.readline()
		self.voltage = float(self.reading[5:9])/1000
		self.pressure = 10 ** (self.voltage-11)
		return self.pressure
		print self.pressure

class HighVacuumDisplay():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.display = PressureReadOut('COM7')
		self.threadDisplay = perpetualTimer(1, self.displayPresure, 'dis')
		self.threadDisplay.start()
		
		#self.readButton = Button(master, text='Read Pressure', command=self.displayPresure)
		#self.readButton.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.pressureVar = DoubleVar()
		self.displayEntry = Entry(master, textvariable=self.pressureVar)
		self.displayEntry.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.displayEntry.configure(state='disabled', font=200)
		self.unitLabel = Label(master, text='mbar')
		self.unitLabel.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.unitLabel.configure(font=200)
		
		
	def displayPresure(self):
		self.pressureValue = self.display.readPresure()
		self.pressureVar.set(self.pressureValue)
	
	def quit(self):
		if tkMessageBox.askokcancel("Exit", "Do you want to exit?"):
			self.master.destroy()
			self.threadDisplay.cancel()
			self.display.closeSerialPort()

root = Tk()
pressure_read_out = HighVacuumDisplay(root)
root.mainloop()