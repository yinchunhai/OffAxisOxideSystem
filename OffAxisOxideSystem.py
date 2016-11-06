from Tkinter import *
import tkMessageBox
import serial
import thread

from BrooksMFC import MFC
from perpetualTimer import perpetualTimer

class OffAxisOxideSystem():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.mfcArgon = MFC('COM12', '8A5A0F462A', 'Ar')
		#self.threadArgon = perpetualTimer(3, self.readArgon)
			
		#self.realflowArgon = self.mfcArgon.readPrimaryValue()
		#self.realflowArgonVar.set(self.realflowArgon)
		
		#Process Gas Frame
		self.processGasFrame = LabelFrame(master, text='Process Gas', padx=5, pady=5)
		self.processGasFrame.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		#row 0
		self.setpointLabel = Label(self.processGasFrame, text='Set Point (%)')
		self.setpointLabel.grid(row=0, column=3, sticky=W, padx=5, pady=5)
		self.setflowLabel = Label(self.processGasFrame, text='Set Flow (ml/min)')
		self.setflowLabel.grid(row=0, column=5, sticky=W, padx=5, pady=5)
		self.realflowLabel = Label(self.processGasFrame, text='Real Flow (ml/min)')
		self.realflowLabel.grid(row=0, column=6, sticky=W, padx=5, pady=5)
		
		#row 1 Argon widgets
		self.checkButtonArgon = Checkbutton(self.processGasFrame, text='Argon') 
		self.checkButtonArgon.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.checkButtonArgon.configure(state='disabled')
		self.enableArgonButton = Button(self.processGasFrame, text='Enable', command=self.enableArgon)
		self.enableArgonButton.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.disableArgonButton = Button(self.processGasFrame, text='Disable', command=self.disableArgon)
		self.disableArgonButton.grid(row=1, column=2, sticky=W, padx=5, pady=5)
		self.setpointArgonVar = DoubleVar()
		self.setflowArgonVar = DoubleVar()
		self.realflowArgonVar = StringVar()
		self.setpointArgonEntry = Entry(self.processGasFrame, textvariable=self.setpointArgonVar)
		self.setpointArgonEntry.grid(row=1, column=3, sticky=W, padx=5, pady=5)
		self.setpointArgonEntry.configure(state='disabled')
		self.setpointArgonButton = Button(self.processGasFrame, text='Set', command=self.setArgon)
		self.setpointArgonButton.grid(row=1, column=4, sticky=W, padx=5, pady=5)
		self.setpointArgonButton.configure(state='disabled')
		self.setflowArgonEntry = Entry(self.processGasFrame, textvariable=self.setflowArgonVar)
		self.setflowArgonEntry.grid(row=1, column=5, sticky=W, padx=5, pady=5)
		self.setflowArgonEntry.configure(state='readonly')
		self.realflowArgonEntry = Entry(self.processGasFrame, textvariable=self.realflowArgonVar)
		self.realflowArgonEntry.grid(row=1, column=6, sticky=W, padx=5, pady=5)
		self.realflowArgonEntry.configure(state='readonly')
		self.offArgonButton = Button(self.processGasFrame, text='Off', command=self.offArgon)
		self.offArgonButton.grid(row=1, column=7, sticky=W, padx=5, pady=5)
		self.offArgonButton.configure(state='disabled')
		self.openArgonButton = Button(self.processGasFrame, text='Open', command=self.openArgon)
		self.openArgonButton.grid(row=1, column=8, sticky=W, padx=5, pady=5)
		self.openArgonButton.configure(state='disabled')
		self.closeArgonButton = Button(self.processGasFrame, text='Close', command=self.closeArgon)
		self.closeArgonButton.grid(row=1, column=9, sticky=W, padx=5, pady=5)
		self.closeArgonButton.configure(state='disabled')
	#Argon Functions
	def enableArgon(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Argon?')
		if result == True:
			self.checkButtonArgon.configure(state='normal')
			self.setpointArgonEntry.configure(state='normal')
			self.setpointArgonButton.configure(state='normal')
			self.offArgonButton.configure(state='normal')
			self.openArgonButton.configure(state='normal')
			self.closeArgonButton.configure(state='normal')
			#self.threadArgon.start()
		else:
			pass
		
	def disableArgon(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Argon?')
		if result == True:
			self.checkButtonArgon.configure(state='disabled')
			self.setpointArgonEntry.configure(state='disabled')
			self.setpointArgonButton.configure(state='disabled')
			self.offArgonButton.configure(state='disabled')
			self.openArgonButton.configure(state='disabled')
			self.closeArgonButton.configure(state='disabled')
		else:
			pass
		
	def setArgon(self):
		self.setpointArgon = float(self.setpointArgonEntry.get())
		self.setflowArgonVar.set(self.setpointArgon*2)
		
	def offArgon(self):
		self.mfcArgon.setValveOverrideOff()
		self.setpointArgon = float(self.setpointArgonEntry.get())
		self.mfcArgon.setFlowSetPointPercentage(self.setpointArgon)
				
		self.realflowArgon = self.mfcArgon.readPrimaryValue()
		self.realflowArgonVar.set(self.realflowArgon)
	
	def openArgon(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to open 100%?')
		if result == True:
			self.mfcArgon.setValveOverrideOpen()
		else:
			pass

	def closeArgon(self):
		self.mfcArgon.setValveOverrideClose()
		
	def readArgon(self):
		self.realflowArgon = self.mfcArgon.readPrimaryValue()
		self.realflowArgonVar.set(self.realflowArgon)
		
	def quit(self):
		if tkMessageBox.askokcancel("Exit", "Do you want to exit?"):
			self.master.destroy()
			#self.threadArgon.cancel()
			self.mfcArgon.closeSerialPort()
			
			

root = Tk()

root.title("Off Axis Oxide System")
oxide = OffAxisOxideSystem(root)
root.mainloop()
