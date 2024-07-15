from gpiozero import DigitalOutputDevice, Button
from time import sleep
import threading
import sys

class treadmill_control():
	def __init__(self):
		self.ser = DigitalOutputDevice(14)
		self.logic = {'0' : self.long_pulse , '1' : self.short_pulse}  # 001=1 and 011=0, bit0 = [0.0016,0.0032], bit1 = [0.0032,0.0016]
		self.const_signalbin = '1001100000000'
		self.l = 1

	def short_pulse(self):
		self.ser.off()
		sleep(0.0032)
		self.ser.on()
		sleep(0.0016)
	
	def long_pulse(self):
		self.ser.off()
		sleep(0.0016)
		self.ser.on()
		sleep(0.0032)
		
	def var_signal(self,level):	
		if self.l >= 0 and self.l <= 8.0:
			self.speed = self.l
			integer = float(level) * 10	
			binary = '101010' + '0' * (7 - len(format(int(integer),'b'))) + format(int(integer),'b')
			for x in range(len(binary)):
				self.logic[binary[x]]()
			
	def pause(self):
		self.ser.off()
		sleep(0.0368)
	
	def const_signal(self):
		for x in range(len(self.const_signalbin)):
			self.logic[self.const_signalbin[x]]()

	def user_input(self):
		while True:
			try:
				self.l = float(input())
			except ValueError:
				print("Not a valid number")


	def input_thread(self):
		self.t = threading.Thread(target=self.user_input)
		self.t.daemon = True
		self.t.start()

	def button_presses(self):
		if self.button.is_pressed:
			if self.terminal_control:
				self.terminal_control = False
			else:
				self.terminal_control = True

	def run(self):
		self.ser.off()
		sleep(1)
		for x in range(0,100,50):	
			self.var_signal(x/100)
			self.pause()
			self.var_signal((x/100) + 0.5)
			self.pause()
			self.const_signal()
			self.pause()
			self.const_signal()
			self.pause()
			print(f"Current level is {x/100}")
		while True:
			self.button_presses()
			if self.terminal_control:	
				if self.l >= 0 and self.l <= 8.0:
					self.var_signal(self.l)
					self.pause()
					self.var_signal(self.l)
					self.pause()
					self.const_signal()
					self.pause()
					self.const_signal()
					self.pause()
					print(f"Current level is {self.l}")
				else: 
					print("You have entered a level which the Treadmill cannot reach(Max is 8)")
					while self.l > 8.0 or self.l < 0:
						self.var_signal(self.speed)
						self.pause()
						self.var_signal(self.speed)
						self.pause()
						self.const_signal()
						self.pause()
						self.const_signal()
						self.pause()
						print(f"Running at {self.speed}")

	def stop(self):
		print("Stopping the Treadmill")
		if self.l >= 0 and self.l <= 8.0:
			for x in range(1,int(self.l) + 1,1):	
				self.var_signal(self.l - float(x))
				self.pause()
				self.var_signal(self.l - float(x))
				self.pause()
				self.const_signal()
				self.pause()
				self.const_signal()
				self.pause()
				print(f"Current level is {self.l - float(x)}")
		else:
			for x in range(1,int(self.speed) + 1,1):	
				self.var_signal(self.speed - float(x))
				self.pause()
				self.var_signal(self.speed - float(x))
				self.pause()
				self.const_signal()
				self.pause()
				self.const_signal()
				self.pause()
				print(f"Current level is {self.speed - float(x)}")
		print("Treadmill has stopped")

try:
	if __name__ == "__main__":
		drive = treadmill_control()
		drive.input_thread()
		drive.run()
except KeyboardInterrupt:
	drive.stop()
	sys.exit()
