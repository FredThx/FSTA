#!/usr/bin/env python
# -*- coding:utf-8 -*

from FSTA.installation import *
from FSTA.action import *
from FSTA.scenario import *
from FUTIL.my_logging import *
import socket
import json

class group(object):
	"""A group of scenarios with a unique hotword
	"""
	max_distance = 5
	min_cosine = 0.4
	def __init__(self, 
					name, 
					hotword = "./resources/hotwords/snowboy.umdl", 
					mqtt_before_topic = None, 
					mqtt_before_s2t_topic = None,
					mqtt_always_topic = None,
					scenarios = [],
					before_actions = [],
					always_actions = [],
					and_words = []):
		"""Initialisation
			- name					:	name of the group
			- hotword				:	string containing path to a umdl or pmdl file as "Ok google" 
			- mqtt_before_topic		:	if set, a mqtt message is send with it as topic and name as message when hotword is detected
			- mqtt_before_s2t_topic :	if set, a mqtt message is send with it as topic and name as message when audio is captured
			- mqtt_always_topic		:	if set, a mqtt message is send with it as topic and name as message when text is reconized
			- scenarios				:	list of scenarios (facultatif : they can be added after as plugins)
			- before_actions		:	list of actions called when the hotword is detected (redundant with mqtt_before_topic), before text detection
			- always_actions		:	list of actions called after the text detection
		"""
		self.name = name
		self.hotword = hotword
		self.scenarios = {}
		self.installation = None
		self.mqtt_before_topic = mqtt_before_topic
		self.mqtt_before_s2t_topic = mqtt_before_s2t_topic
		self.mqtt_always_topic = mqtt_always_topic
		self.before_actions = before_actions
		self.always_actions = always_actions
	
	@property
	def always_actions(self):
		return self._always_actions
	@always_actions.setter
	def always_actions(self, actions):
		if isinstance(actions, list):
			self._always_actions = actions
		else:
			self._always_actions = [actions]
	
	@property
	def before_actions(self):
		return self._before_actions
	@before_actions.setter
	def before_actions(self, actions):
		if isinstance(actions, list):
			self._before_actions = actions
		else:
			self._before_actions = [actions]
	
	
	def init(self, installation):
		'''Initialise the group with installation datas
		'''
		self.installation = installation
		for scenario in self.scenarios.values():
			scenario.init(self)
		if self.mqtt_before_topic == None and installation.mqtt_base_topic :
			self.mqtt_before_topic = installation.mqtt_base_topic + self.name + "/before"
		if self.mqtt_before_s2t_topic == None and installation.mqtt_base_topic :
			self.mqtt_before_s2t_topic = installation.mqtt_base_topic + self.name + "/before_s2t"
		if self.mqtt_always_topic == None and installation.mqtt_base_topic :
			self.mqtt_always_topic = installation.mqtt_base_topic + self.name + "/text"
		for action in self.always_actions:
			action.init(self.installation)
		for action in self.before_actions:
			action.init(self.installation)
	
	def callback(self):
		""" Function called when the hotword match
		"""
		logging.info(self.name + " : I listen ...")
		#Before actions
		if self.mqtt_before_topic:
			self.installation.mqtt_send(self.mqtt_before_topic, self.name)
		if self.before_actions:
			self.run_before_actions()
		#audio detection
		self.installation.on_action = True
		self.installation.detector.terminate()
		self.installation.eyes.open_eye(0)
		self.installation.calibrate()
		self.installation.eyes.open_eye(1)
		self.installation.eyes.vibre()
		time.sleep(0.1)
		text = None
		try:
			with sr.Microphone() as source:
				audio = self.installation.reconizer.listen(source, self.installation.listen_timeout)
			logging.info("Audio captured")
			# Before Speak To Text
			if self.mqtt_before_s2t_topic:
				self.installation.mqtt_send(self.mqtt_before_s2t_topic, self.name)
			self.installation.eyes.show_car("@")
			#Google API
			try:
				text =  self.installation.reconizer.recognize_google(audio, key=self.installation.google_API_key, language = self.installation.language)
				logging.info("Text found with Google API: " + text)
			except sr.UnknownValueError:
				logging.warning("Google Speech Recognition could not understand audio")
			except sr.RequestError as e:
				logging.error("Could not request results from Google Speech Recognition service; {0}".format(e))
			#TODO : utiliser d'autres API
		except Exception as e:
			logging.warning("Audio capture error : %s"%(e.message))
			if self.mqtt_before_s2t_topic:
				self.installation.mqtt_send(self.mqtt_before_s2t_topic, self.name)
		if text:
			texts = re.split(self.installation._and_words,text)
			if len(texts)>1:
				logging.info("Text splited : %s"%(texts))
			for text in texts:
				# language analyser
				best_scenario = self.get_best_scenario(text)
				#Always actions
				self.run_always_actions(text)
				if self.mqtt_always_topic:
						self.installation.mqtt_send(self.mqtt_always_topic, json.dumps({'text':text,'scenario':best_scenario}))
				#Best_scenario(s)
				if best_scenario:
					self.scenarios[best_scenario].run(text)
				else:
					self.installation.show_message("?????")
					logging.info("The text no match with scenarios.")
					time.sleep(0.5)
		else:
			self.installation.show_message("#")
			self.installation.eyes.vibre(1)
			logging.info("None text captured.")
			time.sleep(0.5)
		self.installation.eyes.close_eye()
		
		
	def add_scenario(self,name, phrases = [], actions = [], min_cosine = 0.4, text = None):
		'''add or update a scenario
		'''
		if name in self.scenarios:
			self.scenarios[name].phrases = phrases
			self.scenarios[name].actions = actions
			self.scenarios[name].min_cosine = min_cosine
			self.scenarios[name].text = text
		else:
			self.scenarios[name] = scenario(name, phrases, actions, min_cosine, text)
	
	def allphrases(self):
		''' return a list of tuple : [(text,scenario_name),(..),...]
		'''
		phrases = []
		for index in self.scenarios:
			for text in self.scenarios[index].phrases:
				phrases.append((text, index))
		return phrases
	
	def run_always_actions(self, text):
		'''Run all the always_actions
		'''
		for action in self.always_actions:
			action.run(text)
			
	def run_before_actions(self):
		'''Run all the before_actions
		'''
		for action in self.before_actions:
			action.run()
	
	def get_best_scenario(self, text):
		''' return the name of the best scenario or False
		'''
		texts, scenario_names = zip(*self.allphrases())
		logging.debug(texts)
		logging.debug(scenario_names)
		try:
			cosines = self.installation.language_analyser.get_cosines(text, texts)
		except Exception as e:
			logging.warning("cortical error : %s"%(e.message))
		best_cosine = 0
		best_scenario = False
		for i in range(0,len(cosines)):
			if cosines[i]>self.scenarios[scenario_names[i]].min_cosine:
				if cosines[i]>best_cosine:
					best_scenario = scenario_names[i]
					best_cosine = cosines[i]
		logging.info("Best scénario found : %s with cosine=%s"%(best_scenario, best_cosine))
		return best_scenario
