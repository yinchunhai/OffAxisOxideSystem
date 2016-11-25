from Tkinter import *
import tkMessageBox
from pyduino import *
import time

PIN10 = 10
PIN11 = 11
PIN12 = 12
target1 = 'SmNiO3'
target2 = 'LaAlO3'
target3 = 'SrVO3'
target4 = 'Al2O3'

class SwitchBox():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.switchBox = Arduino()
		time.sleep(3)
		self.switchBox.set_pin_mode(PIN10,'O')
		self.switchBox.set_pin_mode(PIN11,'O')
		self.switchBox.set_pin_mode(PIN12,'O')
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

root = Tk()

root.title("Switch Box")
oxide = SwitchBox(root)
root.mainloop()
