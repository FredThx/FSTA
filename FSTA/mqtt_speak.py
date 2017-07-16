#!/usr/bin/env python
# -*- coding:utf-8 -*

import os
import paho.mqtt.client as mqtt
from FUTIL.my_logging import *
import time

try:
	from gtts import gTTS
except ImportError:
	pass
try:
	import pyttsx
except ImportError:
	pass

class mqtt_speak:
	'''A text via mqtt to speak class
	Usage : mqtt_speak('T-HOME/PI-SALON/SPEAK')
	'''
	def __init__(self, topic, mqtt_host = 'localhost', mqtt_port = '1883', mode = 'gTTS', language = 'fr'):
		'''Initialisation
			topic		:	MQTT topic
			mqtt_host		:	(default = 'localhoct')
			mqtt_port		:	(default = 1883)
			mode			:	'qTTS' for Google Text To Speak or 'pyttsx' for pyttsx 
			language		:	'fr' for french
		'''
		self.topic = topic
		self.mqttc = mqtt.Client()
		self.mqttc.connect(mqtt_host, mqtt_port)
		self.mqttc.on_connect = self.on_mqtt_connect
		self.mqttc.on_disconnect = self.on_mqtt_disconnect
		self.mqttc.message_callback_add(topic, self.on_mqtt_message)
		if mode == 'gTTS':
			self.speaker = gTTS_speaker(language)
		elif mode == 'pyttsx':
			if language == 'fr':
				language = 'french'
			self.speaker = pyttsx_speaker(language) 
		logging.info('mqtt_speak initialised with topic %s on %s:%s. Mode is %s and language %s'%(topic, mqtt_host, mqtt_port, mode, language))
		self.speak("Initialisation de la voix.")
		self.mqttc.loop_forever()

	def speak(self, text):
		'''Speak the text
		'''
		self.speaker.speak(text)

	def on_mqtt_message(self, client, userdata, msg):
		logging.info("MQTT : %s => %s"%(msg.topic, msg.payload))
		self.speak(msg.payload.decode('utf8'))

	def on_mqtt_connect(self, client, userdata, flags, rc):
		logging.info("MQTT connection.")
		self.mqttc.message_callback_add(self.topic, self.on_mqtt_message)
		self.mqttc.subscribe(self.topic)
	
	def on_mqtt_disconnect(self, client, userdata, rc):
		if rc != 0:
			logging.warning("MQTT : Unexpected disconnection.")
			self.mqttc.reconnect()
		else:
			logging.info("MQTT disconnection.")


class speaker:
	'''A Text to Speak class
	'''
	
class gTTS_speaker(speaker):
	''' for google tts
	'''
	def __init__(self, language = 'fr'):
		'''Initialisation
			language		:	ex : 'fr'
		'''	
		self.language = language
		
	def speak(self, text):
		'''Speak the text
		'''
		try:
			gTTS(text=text, lang=self.language).save("tts.mp3")
			os.system('mpg123 tts.mp3')
			logging.info("'%s' speaked with gTTS."%(text))
		except Exception as e:
			logging.warning(e.message)
		
class pyttsx_speaker(speaker):
	'''for pyttsx
	'''
	def __init__(self, language = 'fr', rate = 120):
		'''Initialisation
			language		:	ex : 'fr'
		'''	
		self.engine = pyttsx.init()
		self.engine.setProperty('rate', rate)
		self.engine.setProperty('voice', language)
	
	def speak(self, text):
		'''Speak the text
		'''
		for phrase in text.split('.'):
			if phrase:
				self.engine.say(phrase)
				self.engine.runAndWait()
				time.sleep(0.2)
		logging.info("'%s' speaked with pyttsx."%(text))

#Exemple
if __name__ == '__main__':
	self = mqtt_speak('T-HOME/PI-SALON/SPEAK')
