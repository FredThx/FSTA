#!/usr/bin/env python
# -*- coding:utf-8 -*

from FSTA.mqtt_speak import *
from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = DEBUG, details = False)
mqtt_speak('T-HOME/PI-SALON/SPEAK', mode = 'pyttsx')
