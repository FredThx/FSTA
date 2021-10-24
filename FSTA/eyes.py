#!/usr/bin/env python
# -*- coding:utf-8 -*

import time
import threading
import functools

led_lock = threading.RLock()

def thread(function):
	'''Décorateur : pour executions parallèle
	'''
	@functools.wraps(function)
	def lock_function(*args, **kwargs):
		with led_lock:
			function(*args,**kwargs)
	def th_function(*args, **kwargs):
		th = threading.Thread(None,lock_function,None,args,kwargs)
		th.start()
	return th_function

class eyes(object):
	'''Eyes for FSTA
	'''
	def __init__(self, nb, speed = 2, sleep_timeout = 600):
		self.nb = nb
		self.speed=speed
		self.sleep_timeout = sleep_timeout
		self.sleep_time = sleep_timeout
		self.is_alive = True
		self.sleeper_th = threading.Thread(None, self.sleeper)
		self.sleeper_th.start()

	def __del__(self):
		self.is_alive = False

	def sleeper(self):
		while self.is_alive:
			self.sleep_time -= 1
			if self.sleep_time < 0:
				self.sleep_time = 0
				self.clear()
			else:
				time.sleep(1)

	def sleep_init(self):
		self.sleep_time = self.sleep_timeout

	@property
	def delay(self):
		if self.speed>0:
			return 0.05/self.speed
		else:
			return 0.05

	@thread
	def show_car(self, char, id=None):
		'''Show a charater on one or both eyes
			- char		:	the character
			- id		:	the id of the eye (None : both eyes)
		'''
		self.sleep_init()
		try:
			code = ord(char)
		except:
			code = 32
		text = "["
		for i in range(self.nb):
			if id==None or id == i:
				text += char + "|"
			else:
				text += " |"
		text += "]"
		print(text)

	@thread
	def flash(self, duration = 0.1, intensity = 4):
		'''Increase brightness during duration secondes
			- duration		:	in seconds
			- intensity		:	(1-15)
		'''
		self.sleep_init()
		print(f"Flash eyes during {duration} secondes.")
		time.sleep(duration)

	@thread
	def	vibre(self, duration = 1):
		'''down and up the text
			- duration		in seconds
			- speed			(1-5) speed of mouvement
		'''
		print(f"Vibre eyes during {duration} secondes.")

	@thread
	def clear(self, id=None):
		'''Clear the eyes
			- id	:	id of the eye
		'''
		print(f"Clear eyes.")

	@thread
	def show_message(self, text):
		'''Scroll a text on eyes
		'''
		self.sleep_init()
		print(f"Eyes : <{text}>")
		self.close_eye()

	@thread
	def draw(self, bytes, id = None):
		'''Draw a bytesarray
			- id	:	the id eye
			- bytes	:	a array of bytes
		'''
		for i in range(self.nb):
			if id==None or id==i:
				print(f"Eye {i} :")
				for c in range(8):
					print(f"\t{bytes[c]:08b}")

	@thread
	def open_eye(self, id = None):
		''' Open one or both eyes
			- id	the id eye
		'''
		self.sleep_init()
		print(f"Open eye {'all' if id is None else id}")

	@thread
	def close_eye(self, id = None):
		''' Close one or both eyes
			- id	the id eye
		'''
		self.sleep_init()
		print(f"Open eye {'all' if id is None else id}")

	@thread
	def cligne(self, id = None, delay = None, repeat = 1):
		''' Open one or both eye(s)
			and close it/them
			id		:	the id eye
			delay	:	in seconds
			repeat	:	nb of repetition (None = 1)
		'''
		self.sleep_init()
		if delay==None:
			delay = self.delay*15
		for i in range(repeat):
			self.open_eye(id)
			time.sleep(delay)
			self.close_eye(id)
