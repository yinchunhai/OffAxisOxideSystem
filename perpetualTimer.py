from threading import Timer,Thread,Event

class perpetualTimer():
	def __init__(self,t,hFunction, gas):
		self.t=t
		self.hFunction = hFunction
		self.gas = gas
		self.thread = Timer(self.t,self.handle_function)

	def handle_function(self):
		self.hFunction()
		self.thread = Timer(self.t,self.handle_function)
		self.thread.start()

	def start(self):
		self.thread.start()
		print self.gas, "Thread started!"

	def cancel(self):
		self.thread.cancel()
		print self.gas, "Thread cancelled!"
