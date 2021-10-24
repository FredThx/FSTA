#!/usr/bin/env python
# -*- coding:utf-8 -*

from FSTA.installation import *
from FSTA.cortical_language_analyser import *
from FSTA.eyes import *

def get_installation():
	return installation(
		mqtt_host='192.168.10.155',
		eyes = eyes(2),
		google_API_key = "AIzaSyDtizHAgEhUw5WjW9aRs84GUNk7o-fXwvA",
		mqtt_base_topic = 'T-HOME/FSTA/LISTEN',
		language_analyser = cortical_language_analyser("84c53140-cdb1-11e6-a057-97f4c970893c"),
		and_words = ["et"],
		civility_sentences = [u"s'il te plaît", u"peux-tu"]
		)
