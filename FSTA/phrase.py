#!/usr/bin/env python
# -*- coding:utf-8 -*

from FUTIL.my_logging import *


class phrase(object):
	"""A phrase for invoqing scenario
	"""

	def __init__(self, text , subjects = []):
		"""Initialisation
			- text			:	a string like "Quelle est la température du %s"
			- subjects		:	list of (words or list of synonimous words)
		"""
		self.text = text
		if isinstance(subjects, list):
			self.subjects = subjects
		else:
			self.subjects = [subjects]
		
	