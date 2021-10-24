#!/usr/bin/env python
# -*- coding:utf-8 -*


import paho.mqtt.client as mqtt
from FUTIL.my_logging import *

try:
	import pyttsx
except ImportError:
	try:
		import pyttsx3 as pyttsx
	except ImportError:
		pass
try:
	from gtts import gTTS
	import os
except ImportError:
	pass

my_logging(console_level = DEBUG, logfile_level = DEBUG, details = False)

class speaker(object):
	''' A text to speak class
	'''
	def __init__(self):
		pass
class TTS(object):
	'''A Text To Speak class
	'''
	def __init__(self, language):
		self.language = language

class googleTTS(TTS):
	'''A google TTS class
	'''
	def __init__(self, tmp = 'tts.mp3', language = 'fr', module = None, device = None):
		'''Initialisation
			- tmp		:	tmp file
			- language	:   default : 'fr'
			- module 	:	audio module (None : default audio module, 'alsa' : alsa module)
			- device	:	audio device (None : default device, 'hw:2,0' : alsa device n° 2, sous-périphérique #0)
		'''
		self.tmp=tmp
		TTS.__init__(self,language)
		self.cmd = f"mpg123{f' -o {module}' if module else ''}{f' -a {device}' if device else ''}"

	def speak(self, text):
		'''Speak the text
		'''
		#TODO : faire mieux (en paralele gTTS et mpg123
		for text in text.split('.'):
			try:
				gTTS(text=text, lang=self.language).save(self.tmp)
				os.system(f'mpg123 {self.tmp}')
				logging.info("'%s' speaked with gTTS."%(text))
			except Exception as e:
				logging.warning(e)

class localTTS(TTS):
	''' A local tts
	'''
	def __init__(self, language = 'french', rate = 120):
		'''Initialisation
			- language
			- rate
		'''
		TTS.__init__(self,language)
		self.engine = pyttsx.init()
		self.engine.setProperty('rate', rate)
		self.engine.setProperty('voice', language)

	def speak(self, text):
		self.engine.say(text)
		self.engine.runAndWait()
		logging.info("'%s' speaked with pyttsx."%(text))

class mqtt_speaker(speaker):
	''' A mqtt-test to speak class
	'''
	def __init__(self, tts, topic, mqtt_host, mqtt_port=1883):
		'''Initialisation
			- tts 			TTS object
			- topic to subscribe
			- mqtt_host
			- mqtt_port
		'''
		self.tts = tts
		self.topic = topic
		self.mqtt_host = mqtt_host
		self.mqtt_port = mqtt_port
		self.mqttc = mqtt.Client()
		self.mqttc.on_connect = self.on_mqtt_connect
		self.mqttc.on_disconnect = self.on_mqtt_disconnect
		#self.mqttc.message_callback_add(self.topic, self.on_mqtt_message)

	def run(self):
		''' Run forever
		'''
		self.mqttc.connect(mqtt_host, mqtt_port)
		self.tts.speak("Salut les amis. Je suis a votre service.")
		self.mqttc.loop_forever()


	def on_mqtt_message(self, client, userdata, msg):
		'''Speak on mqtt reception
		'''
		logging.info("MQTT : %s => %s"%(msg.topic, msg.payload))
		speak(msg.payload)

	def on_mqtt_connect(self, client, userdata, flags, rc):
		''' Subscribe self.topic when mqtt connected
		'''
		logging.info("MQTT connection.")
		mqttc.message_callback_add(self.topic, self.on_mqtt_message)
		mqttc.subscribe(self.topic)

	def on_mqtt_disconnect(client, userdata, rc):
		''' Reconnect when connection fail
		'''
		if rc != 0:
			logging.warning("MQTT : Unexpected disconnection.")
			mqttc.reconnect()
		else:
			logging.info("MQTT disconnection.")


if __name__ == '__main__':
	speaker = mqtt_speaker(googleTTS(),'T-HOME/PI-SALON/SPEAK','192.168.10.155')
	speaker.run()
