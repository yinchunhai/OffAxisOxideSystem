from Tkinter import *
import tkMessageBox
from pyduino import *
import time
from perpetualTimer import perpetualTimer

PIN10 = 10
PIN11 = 11
PIN12 = 12
PIN17 = 17 #analog output A3
target1 = 'SmNiO3'
target2 = 'LaAlO3'
target3 = 'SrVO3'
target4 = 'Al2O3'

class SwitchBox():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.on_time = 0
		self.off_time = 0

		self.switchBox = Arduino()
		time.sleep(3)
		self.switchBox.set_pin_mode(PIN10,'O')
		self.switchBox.set_pin_mode(PIN11,'O')
		self.switchBox.set_pin_mode(PIN12,'O')
		self.switchBox.set_pin_mode(PIN17,'O')
		time.sleep(1)
		
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
			self.pulseThread = perpetualTimer(0, self.outputPulse, 'Pulse')
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
			self.pulseThread.cancel()

root = Tk()

root.title("Switch Box")
oxide = SwitchBox(root)
root.mainloop()
