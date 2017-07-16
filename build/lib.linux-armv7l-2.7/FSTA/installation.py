#!/usr/bin/env python
# -*- coding:utf-8 -*


import sys
import signal
import time
import paho.mqtt.client as paho
import threading
import logging
import speech_recognition as sr
import snowboydecoder
import os
import re
from FSTA.plugin import *
from FSTA.group import *
from FSTA.fred_language_analyser import *
from FSTA.eyes import *

#TODO : plusieurs API (google, MS, ...) pour gérer quotas

class installation(object):
	"""A complete installation containing :
		- groups of scenarios with unique start hotword
		- mqtt serveur
	"""
	plugin_path = "resources/rules"
	
	def __init__(self, groups = [], 
					mqtt_host='localhost', 
					mqtt_port = 1883, 
					google_API_key = None, 
					language = 'fr-FR', 
					eyes = None, 
					mqtt_base_topic = None, 
					listen_timeout = 5, 
					language_analyser = fred_language_analyser(), 
					and_words = []):
		"""Initialisation
			- groups			:	list of groups of scenarios
			- mqtt_host		:	mqtt host (default localhost)
			- mqtt_port		:	mqtt port (default 1883)
			- google_API_key	:	google API key (32 car)
			- language		:	language for reconition (default : fr-Fr)
			- led			:	a max7219.led
			- and_words		:	list of words for spliting sentences (ex : 'et')
		"""
		self.eyes = eyes
		self.eyes.show_message("* Hello *")
		self.eyes.cligne(repeat=5)
		self.groups = {}
		self.hotwords = []
		self.callbacks = []
		self.mqtt_base_topic = mqtt_base_topic
		if self.mqtt_base_topic:
			if self.mqtt_base_topic[-1]!='/':
				self.mqtt_base_topic = self.mqtt_base_topic + '/'
		self.mqtt_client = paho.Client()
		try:
			self.mqtt_client.connect(mqtt_host, mqtt_port, 30)
		except socket.error:
			logging.error("Mqtt server : Connection refused")
		self.interrupted = False
		self.on_action = False
		self.google_API_key = google_API_key
		self.listen_timeout = listen_timeout
		self.language = language
		self.reconizer = sr.Recognizer()
		self.plugins = {}
		self.language_analyser = language_analyser
		self.and_words = and_words
		
	@property
	def and_words(self):
		return [t[1:-1] for t in self._and_words.split('|')]
	@and_words.setter
	def and_words(self, words):
		if isinstance(words, list):
			self._and_words = " " + " | ".join(words) + " "
		else:
			self._and_words = " " + words + " "
		
	def run(self):
		"""Main function : wait for hotwords and run the callback function for the groups
		"""
		signal.signal(signal.SIGINT, self.signal_handler)
		while not self.interrupted:
			self.check_plugin()
			self.detector = snowboydecoder.HotwordDetector(self.hotwords, sensitivity=0.5*len(self.hotwords))
			logging.debug("Detector start")
			self.on_action = False
			self.detector.start(detected_callback=self.callbacks,interrupt_check=self.interrupt_callback,sleep_time=0.03)
			logging.debug("Detector stopped")
		self.detector.terminate()
		self.eyes.clear()
	
	def signal_handler(self, signal, frame):
		logging.info("installation interrupted by signal.")
		self.interrupted = True
	
	def interrupt_callback(self):
		return self.interrupted or self.on_action
		
	def calibrate(self):
		''' Calibrate the speech_recognition
		'''
		#Une autre solution est recognizer_instance.dynamic_energy_threshold = True (à voir...)
		with sr.Microphone() as source:
			logging.info("Calibration started ...")
			energy = self.reconizer.energy_threshold
			self.reconizer.adjust_for_ambient_noise(source)
			self.reconizer.energy_threshold = max(self.reconizer.energy_threshold, 200)
			logging.info("energy_threshold is changed from %i to %i"%(energy, self.reconizer.energy_threshold))
	
	def check_plugin(self):
		'''Check if new or modiffied plugin and load them if needed.
		'''
		logging.debug("Check plugins...")
		modifs = False
		for file in sorted(os.listdir(installation.plugin_path), key = lambda f:f.split('.')[-1]):
			if file not in self.plugins:
				self.plugins[file] = plugin(file)
				self.plugins[file].load(self)
				modifs = True
			elif self.plugins[file].loaded_date < os.stat(installation.plugin_path + '/' + file).st_mtime:
				self.plugins[file].load(self)
				modifs = True
		if modifs:
			self.hotwords = []
			self.callbacks = []
			for group in self.groups.values():
				self.hotwords.append(group.hotword)
				self.callbacks.append(group.callback)
				group.init(self)
	
	def add_group(self, group_name, hotword, mqtt_hotword_topic = None):
		'''Add or update a group to the installation
		'''
		if group_name in self.groups:
			self.groups[group_name].hotword = hotword
			self.groups[group_name].mqtt_hotword_topic = mqtt_hotword_topic
		else:
			self.groups[group_name] = group(group_name,hotword, mqtt_hotword_topic)
	
	def add_scenario(self, group_name, name, phrases = [] , actions = []):
		'''Add or update a scenario
		'''
		if group_name in self.groups:
			self.groups[group_name].add_scenario(name, phrases, actions)
		else:
			logging.error("Group %s is not declare.")
	
	def group(self, group_name):
		'''Return a group
		'''
		return self.groups[group_name]
	
	def allphrases(self):
		'''to debug
		'''
		phrases = []
		for group in self.groups.values():
			for scenario in group.scenarios.values():
				phrases.extend(scenario.phrases)
		return phrases
	
	def show_message(self, text):
		'''Show message on the leds (tread)
		'''
		self.eyes.show_message(text)
	
	def mqtt_send(self, topic, payload):
		'''Send a mqtt message
		'''
		logging.debug("MQTT SEND topic : %s , payload : %s"%(topic, payload))
		try:
			self.mqtt_client.reconnect()
			self.mqtt_client.publish(topic, payload)
		except socket.error:
			logging.error("Mqtt server : Connection refused")
