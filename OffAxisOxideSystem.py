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
		self.threadArgon = perpetualTimer(3, self.readArgon, 'Ar')
		self.mfcOxygen = MFC('COM13', '8A5A0F4A11', 'O2')
		self.threadOxygen = perpetualTimer(3, self.readOxygen, 'O2')
		self.mfcNitrogen = MFC('COM11', '8A5ABA8529', 'N2')
		self.threadNitrogen = perpetualTimer(3, self.readNitrogen, 'N2')
		
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
		#row 2 Oxygen widgets
		self.checkButtonOxygen = Checkbutton(self.processGasFrame, text='Oxygen') 
		self.checkButtonOxygen.grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.checkButtonOxygen.configure(state='disabled')
		self.enableOxygenButton = Button(self.processGasFrame, text='Enable', command=self.enableOxygen)
		self.enableOxygenButton.grid(row=2, column=1, sticky=W, padx=5, pady=5)
		self.disableOxygenButton = Button(self.processGasFrame, text='Disable', command=self.disableOxygen)
		self.disableOxygenButton.grid(row=2, column=2, sticky=W, padx=5, pady=5)
		self.setpointOxygenVar = DoubleVar()
		self.setflowOxygenVar = DoubleVar()
		self.realflowOxygenVar = StringVar()
		self.setpointOxygenEntry = Entry(self.processGasFrame, textvariable=self.setpointOxygenVar)
		self.setpointOxygenEntry.grid(row=2, column=3, sticky=W, padx=5, pady=5)
		self.setpointOxygenEntry.configure(state='disabled')
		self.setpointOxygenButton = Button(self.processGasFrame, text='Set', command=self.setOxygen)
		self.setpointOxygenButton.grid(row=2, column=4, sticky=W, padx=5, pady=5)
		self.setpointOxygenButton.configure(state='disabled')
		self.setflowOxygenEntry = Entry(self.processGasFrame, textvariable=self.setflowOxygenVar)
		self.setflowOxygenEntry.grid(row=2, column=5, sticky=W, padx=5, pady=5)
		self.setflowOxygenEntry.configure(state='readonly')
		self.realflowOxygenEntry = Entry(self.processGasFrame, textvariable=self.realflowOxygenVar)
		self.realflowOxygenEntry.grid(row=2, column=6, sticky=W, padx=5, pady=5)
		self.realflowOxygenEntry.configure(state='readonly')
		self.offOxygenButton = Button(self.processGasFrame, text='Off', command=self.offOxygen)
		self.offOxygenButton.grid(row=2, column=7, sticky=W, padx=5, pady=5)
		self.offOxygenButton.configure(state='disabled')
		self.openOxygenButton = Button(self.processGasFrame, text='Open', command=self.openOxygen)
		self.openOxygenButton.grid(row=2, column=8, sticky=W, padx=5, pady=5)
		self.openOxygenButton.configure(state='disabled')
		self.closeOxygenButton = Button(self.processGasFrame, text='Close', command=self.closeOxygen)
		self.closeOxygenButton.grid(row=2, column=9, sticky=W, padx=5, pady=5)
		self.closeOxygenButton.configure(state='disabled')
		#row 3 Nitrogen Functions
		self.checkButtonNitrogen = Checkbutton(self.processGasFrame, text='Nitrogen') 
		self.checkButtonNitrogen.grid(row=3, column=0, sticky=W, padx=5, pady=5)
		self.checkButtonNitrogen.configure(state='disabled')
		self.enableNitrogenButton = Button(self.processGasFrame, text='Enable', command=self.enableNitrogen)
		self.enableNitrogenButton.grid(row=3, column=1, sticky=W, padx=5, pady=5)
		self.disableNitrogenButton = Button(self.processGasFrame, text='Disable', command=self.disableNitrogen)
		self.disableNitrogenButton.grid(row=3, column=2, sticky=W, padx=5, pady=5)
		self.setpointNitrogenVar = DoubleVar()
		self.setflowNitrogenVar = DoubleVar()
		self.realflowNitrogenVar = StringVar()
		self.setpointNitrogenEntry = Entry(self.processGasFrame, textvariable=self.setpointNitrogenVar)
		self.setpointNitrogenEntry.grid(row=3, column=3, sticky=W, padx=5, pady=5)
		self.setpointNitrogenEntry.configure(state='disabled')
		self.setpointNitrogenButton = Button(self.processGasFrame, text='Set', command=self.setNitrogen)
		self.setpointNitrogenButton.grid(row=3, column=4, sticky=W, padx=5, pady=5)
		self.setpointNitrogenButton.configure(state='disabled')
		self.setflowNitrogenEntry = Entry(self.processGasFrame, textvariable=self.setflowNitrogenVar)
		self.setflowNitrogenEntry.grid(row=3, column=5, sticky=W, padx=5, pady=5)
		self.setflowNitrogenEntry.configure(state='readonly')
		self.realflowNitrogenEntry = Entry(self.processGasFrame, textvariable=self.realflowNitrogenVar)
		self.realflowNitrogenEntry.grid(row=3, column=6, sticky=W, padx=5, pady=5)
		self.realflowNitrogenEntry.configure(state='readonly')
		self.offNitrogenButton = Button(self.processGasFrame, text='Off', command=self.offNitrogen)
		self.offNitrogenButton.grid(row=3, column=7, sticky=W, padx=5, pady=5)
		self.offNitrogenButton.configure(state='disabled')
		self.openNitrogenButton = Button(self.processGasFrame, text='Open', command=self.openNitrogen)
		self.openNitrogenButton.grid(row=3, column=8, sticky=W, padx=5, pady=5)
		self.openNitrogenButton.configure(state='disabled')
		self.closeNitrogenButton = Button(self.processGasFrame, text='Close', command=self.closeNitrogen)
		self.closeNitrogenButton.grid(row=3, column=9, sticky=W, padx=5, pady=5)
		self.closeNitrogenButton.configure(state='disabled')
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
			self.threadArgon.start()
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
		print "Argon flow is:", self.realflowArgon
		
	#Oxygen Functions
	def enableOxygen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Oxygen?')
		if result == True:
			self.checkButtonOxygen.configure(state='normal')
			self.setpointOxygenEntry.configure(state='normal')
			self.setpointOxygenButton.configure(state='normal')
			self.offOxygenButton.configure(state='normal')
			self.openOxygenButton.configure(state='normal')
			self.closeOxygenButton.configure(state='normal')
			self.threadOxygen.start()
		else:
			pass
	
	def disableOxygen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Oxygen?')
		if result == True:
			self.checkButtonOxygen.configure(state='disabled')
			self.setpointOxygenEntry.configure(state='disabled')
			self.setpointOxygenButton.configure(state='disabled')
			self.offOxygenButton.configure(state='disabled')
			self.openOxygenButton.configure(state='disabled')
			self.closeOxygenButton.configure(state='disabled')
		else:
			pass
		
	def setOxygen(self):
		self.setpointOxygen = float(self.setpointOxygenEntry.get())
		self.setflowOxygenVar.set(self.setpointOxygen*2)
		
	def offOxygen(self):
		self.mfcOxygen.setValveOverrideOff()
		self.setpointOxygen = float(self.setpointOxygenEntry.get())
		self.mfcOxygen.setFlowSetPointPercentage(self.setpointOxygen)
		
	def openOxygen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to open 100%?')
		if result == True:
			self.mfcOxygen.setValveOverrideOpen()
		else:
			pass

	def closeOxygen(self):
		self.mfcOxygen.setValveOverrideClose()
		
	def readOxygen(self):
		self.realflowOxygen = self.mfcOxygen.readPrimaryValue()
		self.realflowOxygenVar.set(self.realflowOxygen)
		print "Oxygen flow is:", self.realflowOxygen
	
	#Nitrogen Functions
	def enableNitrogen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Nitrogen?')
		if result == True:
			self.checkButtonNitrogen.configure(state='normal')
			self.setpointNitrogenEntry.configure(state='normal')
			self.setpointNitrogenButton.configure(state='normal')
			self.offNitrogenButton.configure(state='normal')
			self.openNitrogenButton.configure(state='normal')
			self.closeNitrogenButton.configure(state='normal')
			self.threadNitrogen.start()
		else:
			pass
	
	def disableNitrogen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Nitrogen?')
		if result == True:
			self.checkButtonNitrogen.configure(state='disabled')
			self.setpointNitrogenEntry.configure(state='disabled')
			self.setpointNitrogenButton.configure(state='disabled')
			self.offNitrogenButton.configure(state='disabled')
			self.openNitrogenButton.configure(state='disabled')
			self.closeNitrogenButton.configure(state='disabled')
		else:
			pass
		
	def setNitrogen(self):
		self.setpointNitrogen = float(self.setpointNitrogenEntry.get())
		self.setflowNitrogenVar.set(self.setpointNitrogen*2)
		
	def offNitrogen(self):
		self.mfcNitrogen.setValveOverrideOff()
		self.setpointNitrogen = float(self.setpointNitrogenEntry.get())
		self.mfcNitrogen.setFlowSetPointPercentage(self.setpointNitrogen)
		
	def openNitrogen(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to open 100%?')
		if result == True:
			self.mfcNitrogen.setValveOverrideOpen()
		else:
			pass

	def closeNitrogen(self):
		self.mfcNitrogen.setValveOverrideClose()
		
	def readNitrogen(self):
		self.realflowNitrogen = self.mfcNitrogen.readPrimaryValue()
		self.realflowNitrogenVar.set(self.realflowNitrogen)
		print "Nitrogen flow is:", self.realflowNitrogen
	
	def quit(self):
		if tkMessageBox.askokcancel("Exit", "Do you want to exit?"):
			self.master.destroy()
			self.threadArgon.cancel()
			self.mfcArgon.closeSerialPort()
			
			

root = Tk()

root.title("Off Axis Oxide System")
oxide = OffAxisOxideSystem(root)
root.mainloop()
