#!/usr/bin/env python
# -*- coding:utf-8 -*

from FSTA.installation import *
from FSTA.cortical_language_analyser import *
from FSTA.eyes import *

def get_installation():
	return installation(
		mqtt_host='127.0.0.1',
		eyes = eyes(2),
		google_API_key = "AIzaSyDtizHAgEhUw5WjW9aRs84GUNk7o-fXwvA",
		mqtt_base_topic = 'T-HOME/SALON/LISTEN',
		language_analyser = cortical_language_analyser("84c53140-cdb1-11e6-a057-97f4c970893c"),
		and_words = ["et"]
		)
