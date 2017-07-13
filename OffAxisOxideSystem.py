from Tkinter import *
import tkMessageBox
import serial
import thread
import time

from BrooksMFC import MFC
from perpetualTimer import perpetualTimer
from pyduino import *

PIN10 = 10
PIN11 = 11
PIN12 = 12
PIN17 = 17 #analog output A3
target1 = 'SmNiO3'
target2 = 'LaAlO3'
target3 = '???'
target4 = 'Al2O3'

class OffAxisOxideSystem():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.on_time = 0
		self.off_time = 0
		self.pulseThread = perpetualTimer(0, self.outputPulse, 'Pulse')
		
		self.switchBox = Arduino()
		time.sleep(3)
		self.switchBox.set_pin_mode(PIN10,'O')
		self.switchBox.set_pin_mode(PIN11,'O')
		self.switchBox.set_pin_mode(PIN12,'O')
		self.switchBox.set_pin_mode(PIN17,'O')
		time.sleep(1)
		
		self.mfcArgon = MFC('COM12', '8A5A0F462A', 'Ar')
		self.threadArgon = perpetualTimer(3, self.readArgon, 'Ar')
		self.mfcOxygen = MFC('COM13', '8A5A0F4A11', 'O2')
		self.threadOxygen = perpetualTimer(3, self.readOxygen, 'O2')
		self.mfcNitrogen = MFC('COM11', '8A5ABA8529', 'N2')
		self.threadNitrogen = perpetualTimer(3, self.readNitrogen, 'N2')

		#SwitchBox Frame
		self.switchBoxFrame = LabelFrame(master, text='Switch Box', padx=5, pady=5)
		self.switchBoxFrame.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.targetOneButton = Button(self.switchBoxFrame, text='Target 1\n\n'+target1, command=self.connectTargetOne)
		self.targetOneButton.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.targetTwoButton = Button(self.switchBoxFrame, text='Target 2\n\n'+target2, command=self.connectTargetTwo)
		self.targetTwoButton.grid(row=0, column=1, sticky=W, padx=5, pady=5)
		self.targetThreeButton = Button(self.switchBoxFrame, text='Target 3\n\n'+target3, command=self.connectTargetThree)
		self.targetThreeButton.grid(row=0, column=2, sticky=W, padx=5, pady=5)
		self.targetFourButton = Button(self.switchBoxFrame, text='Target 4\n\n'+target4, command=self.connectTargetFour)
		self.targetFourButton.grid(row=0, column=3, sticky=W, padx=5, pady=5)
		
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
		
		#PulseSputter Frame
		self.pulseSputterFrame = LabelFrame(master, text='Pulse Sputter', padx=5, pady=5)
		self.pulseSputterFrame.grid(row=2, column=0, sticky=W, padx=5, pady=5)
		#row 0
		self.pulseFrequencyLabel = Label(self.pulseSputterFrame, text='Pulse Frequency (Hz)')
		self.pulseFrequencyLabel.grid(row=0, column=2, sticky=W, padx=5, pady=5)
		self.setPulseWidthLabel = Label(self.pulseSputterFrame, text='Set Pulse Width (%)')
		self.setPulseWidthLabel.grid(row=0, column=3, sticky=W, padx=5, pady=5)
		self.realPulseWidthLabel = Label(self.pulseSputterFrame, text='Real Pulse Width (s)')
		self.realPulseWidthLabel.grid(row=0, column=5, sticky=W, padx=5, pady=5)
		#row 1
		self.enablePulseButton = Button(self.pulseSputterFrame, text='Enable', command=self.enablePulse)
		self.enablePulseButton.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.disablePulseButton = Button(self.pulseSputterFrame, text='Disable', command=self.disablePulse)
		self.disablePulseButton.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.pulseFrequencyVarLable = Label(self.pulseSputterFrame, text='1')
		self.pulseFrequencyVarLable.grid(row=1, column=2, sticky=W, padx=5, pady=5)
		self.setPulseWidthVar = DoubleVar()		
		self.setPulseWidthEntry = Entry(self.pulseSputterFrame, textvariable=self.setPulseWidthVar)
		self.setPulseWidthEntry.grid(row=1, column=3, sticky=W, padx=5, pady=5)
		self.setPulseWidthEntry.configure(state='disabled')
		self.setPeriodPulseWidthButton = Button(self.pulseSputterFrame, text='Set', command=self.setPeriodPulseWidth)
		self.setPeriodPulseWidthButton.grid(row=1, column=4, sticky=W, padx=5, pady=5)
		self.setPeriodPulseWidthButton.configure(state='disabled')
		self.realPulseWidthVar = StringVar()
		self.realPulseWidthEntry = Entry(self.pulseSputterFrame, textvariable=self.realPulseWidthVar)
		self.realPulseWidthEntry.grid(row=1, column=5, sticky=W, padx=5, pady=5)
		self.realPulseWidthEntry.configure(state='readonly')		
		self.startPulseButton = Button(self.pulseSputterFrame, text='Start Pulse', command=self.startPulse)
		self.startPulseButton.grid(row=1, column=6, sticky=W, padx=5, pady=5)
		self.startPulseButton.configure(state='disabled')
		self.stopPulseButton = Button(self.pulseSputterFrame,text='Stop Pulse', command=self.stopPulse)
		self.stopPulseButton.grid(row=1, column=7, sticky=W, padx=5, pady=5)
		self.stopPulseButton.configure(state='disabled')
	
	#Pulse functions
	def enablePulse(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Pusle Sputter?')
		if result == True:
			self.enablePulseButton.configure(background='green')
			self.setPulseWidthEntry.configure(state='normal')
			self.setPeriodPulseWidthButton.configure(state='normal')
			self.startPulseButton.configure(state='normal')
			self.stopPulseButton.configure(state='normal')
		else:
			pass
	def disablePulse(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to disable Pulse Sputter?')
		if result == True:
			self.enablePulseButton.configure(background='grey')
			self.setPulseWidthEntry.configure(state='disabled')
			self.setPeriodPulseWidthButton.configure(state='disabled')
			self.startPulseButton.configure(state='disabled')
			self.stopPulseButton.configure(state='disabled')
		else:
			pass
	def setPeriodPulseWidth(self):
		self.setPulseWidth = float(self.setPulseWidthEntry.get())
		self.realPulseWidth = 1 * self.setPulseWidth / 100
		self.realPulseWidthVar.set(self.realPulseWidth)
		print 'Pulse Width is:', self.realPulseWidth, ' second'
		self.on_time = self.realPulseWidth
		self.off_time = 1 - self.realPulseWidth
		return self.on_time
		return self.off_time
	def outputPulse(self):
		self.switchBox.digital_write(PIN17,1)
		time.sleep(self.on_time)
		self.switchBox.digital_write(PIN17,0)		
		time.sleep(self.off_time)
	def startPulse(self):
		print 'On time is: ', self.on_time, 'second'
		print 'Off time is: ', self.off_time, 'second'
		result = tkMessageBox.askyesno('Question', 'Do you want to start pulse?')
		if result == True:
			self.pulseThread.start()
		else:
			pass
	def stopPulse(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to stop pulse?')
		if result == True:
			self.switchBox.digital_write(PIN17,0)
			self.pulseThread.cancel()
		else:
			pass
			
	#Argon Functions
	def enableArgon(self):
		result = tkMessageBox.askyesno('Question', 'Do you want to enable Argon?')
		if result == True:
			self.enableArgonButton.configure(background='green')
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
		result = tkMessageBox.askyesno('Question', 'Do you want to disable Argon?')
		if result == True:
			self.enableArgonButton.configure(background='grey')
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
			self.enableOxygenButton.configure(background='green')
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
		result = tkMessageBox.askyesno('Question', 'Do you want to disable Oxygen?')
		if result == True:
			self.enableOxygenButton.configure(background='grey')
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
		self.setflowOxygenVar.set(self.setpointOxygen)
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
			self.enableNitrogenButton.configure(background='green')
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
		result = tkMessageBox.askyesno('Question', 'Do you want to disable Nitrogen?')
		if result == True:
			self.enableNitrogenButton.configure(background='grey')
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

	#SwitchBox Functions
	def connectTargetOne(self):
		result = tkMessageBox.askquestion('Quiry', 'Do u want to switch to Target 1?')
		if result == 'yes':
			self.switchBox.digital_write(PIN10,0)
			self.switchBox.digital_write(PIN11,0)
			self.switchBox.digital_write(PIN12,0)
			self.targetOneButton.configure(background='green')
			self.targetTwoButton.configure(background='grey')
			self.targetThreeButton.configure(background='grey')
			self.targetFourButton.configure(background='grey')
		else:
			pass
	def connectTargetTwo(self):
		result = tkMessageBox.askquestion('Quiry', 'Do u want to switch to Target 2?')
		if result == 'yes':
			self.switchBox.digital_write(PIN10,1)
			self.switchBox.digital_write(PIN11,0)
			self.switchBox.digital_write(PIN12,0)
			self.targetOneButton.configure(background='grey')
			self.targetTwoButton.configure(background='green')
			self.targetThreeButton.configure(background='grey')
			self.targetFourButton.configure(background='grey')
		else:
			pass
	def connectTargetThree(self):
		result = tkMessageBox.askquestion('Quiry', 'Do u want to switch to Target 3?')
		if result == 'yes':
			self.switchBox.digital_write(PIN10,1)
			self.switchBox.digital_write(PIN11,1)
			self.switchBox.digital_write(PIN12,0)
			self.targetOneButton.configure(background='grey')
			self.targetTwoButton.configure(background='grey')
			self.targetThreeButton.configure(background='green')
			self.targetFourButton.configure(background='grey')
		else:
			pass
	def connectTargetFour(self):
		result = tkMessageBox.askquestion('Quiry', 'Do u want to switch to Target 4?')
		if result == 'yes':
			self.switchBox.digital_write(PIN10,1)
			self.switchBox.digital_write(PIN11,1)
			self.switchBox.digital_write(PIN12,1)
			self.targetOneButton.configure(background='grey')
			self.targetTwoButton.configure(background='grey')
			self.targetThreeButton.configure(background='grey')
			self.targetFourButton.configure(background='green')
		else:
			pass

	def quit(self):
		if tkMessageBox.askokcancel("Exit", "Do you want to exit?"):
			self.master.destroy()
			self.threadArgon.cancel()
			self.mfcArgon.closeSerialPort()
			self.threadOxygen.cancel()
			self.mfcOxygen.closeSerialPort()
			self.threadNitrogen.cancel()
			self.mfcNitrogen.closeSerialPort()
			self.pulseThread.cancel()

root = Tk()

root.title("Off Axis Oxide System")
oxide = OffAxisOxideSystem(root)
root.mainloop()
