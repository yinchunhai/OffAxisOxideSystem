from Tkinter import *
import tkMessageBox

#from ButterFlyValve import ButterFlyValve

class valveTkinter():
	def __init__(self, master):
		self.master = master
		self.master.protocol('WM_DELETE_WINDOW', self.quit)
		
		#self.bfv = ButterFlyValve('COM1')
	
		#ButterFlyValve Frame
		self.bfvFrame = LabelFrame(master, text='Butterfly Valve', padx=5, pady=5)
		self.bfvFrame.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		
		#main Frame
		self.bfvMainFrame = LabelFrame(self.bfvFrame, text='Main Control', padx=5, pady=5)
		self.bfvMainFrame.grid(row=0, column=0, sticky=NW, padx=5, pady=5)
		self.openButton = Button(self.bfvMainFrame, text='Open')
		self.openButton.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.closeButton = Button(self.bfvMainFrame, text='Close')
		self.closeButton.grid(row=1, column=0, sticky=W, padx=5, pady=5)		
		self.holdButton = Button(self.bfvMainFrame, text='Hold')
		self.holdButton.grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.oneQuarterOpenButton = Button(self.bfvMainFrame, text='25%')
		self.oneQuarterOpenButton.grid(row=0, column=1, sticky=W, padx=5, pady=5)
		self.twoQuarterOpenButton = Button(self.bfvMainFrame, text='50%')
		self.twoQuarterOpenButton.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.thrQuarterOpenButton = Button(self.bfvMainFrame, text='75%')
		self.thrQuarterOpenButton.grid(row=2, column=1, sticky=W, padx=5, pady=5)
		#position Frame
		self.bfvPositionFrame = LabelFrame(self.bfvFrame, text='Position Control', padx=5, pady=5)
		self.bfvPositionFrame.grid(row=0, column=1, sticky=NW, padx=5, pady=5)
		self.actualPositionLabel = Label(self.bfvPositionFrame, text='Actual Position')
		self.actualPositionLabel.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.actualPositionEntry = Entry(self.bfvPositionFrame)
		self.actualPositionEntry.grid(row=0, column=1, sticky=W, padx=5, pady=5)
		self.actualPositionEntry.configure(state='readonly')
		self.targetPositionLabel = Label(self.bfvPositionFrame, text='Target Position')
		self.targetPositionLabel.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.targetPositionEntry = Entry(self.bfvPositionFrame)
		self.targetPositionEntry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.targetPositionEntry.configure(state='readonly')
		self.setPositionButton = Button(self.bfvPositionFrame, text='Set Position')
		self.setPositionButton.grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.setPositionEntry = Entry(self.bfvPositionFrame)
		self.setPositionEntry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
		#pressure Frame
		self.bfvPressureFrame = LabelFrame(self.bfvFrame, text='Pressure Control', padx=5, pady=5)
		self.bfvPressureFrame.grid(row=0, column=2, sticky=NW, padx=5, pady=5)
		self.actualPressureLabel = Label(self.bfvPressureFrame, text='Actual Pressure')
		self.actualPressureLabel.grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.actualPressureEntry = Entry(self.bfvPressureFrame)
		self.actualPressureEntry.grid(row=0, column=1, sticky=W, padx=5, pady=5)
		self.actualPressureEntry.configure(state='readonly')
		self.targetPressureLabel = Label(self.bfvPressureFrame, text='Target Pressure')
		self.targetPressureLabel.grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.targetPressureEntry = Entry(self.bfvPressureFrame)
		self.targetPressureEntry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.targetPressureEntry.configure(state='readonly')
		self.setPressureButton = Button(self.bfvPressureFrame, text='Set Pressure')
		self.setPressureButton.grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.setPressureEntry = Entry(self.bfvPressureFrame)
		self.setPressureEntry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
		
		
		
		
		#pressure Frame
		self.bfvPressureFrame = LabelFrame(self.bfvFrame, text='Pressure', padx=5, pady=5)
		self.bfvPressureFrame.grid(row=0, column=2, sticky=W, padx=5, pady=5)
	
	def quit(self):
		if tkMessageBox.askokcancel("Exit", "Do you want to exit?"):
			self.master.destroy()

			
			

root = Tk()

root.title("Butterfly Valve")
oxide = valveTkinter(root)
root.mainloop()