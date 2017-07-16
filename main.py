#!/usr/bin/env python
# -*- coding:utf-8 -*

from FUTIL.my_logging import *

my_logging(console_level = DEBUG, logfile_level = DEBUG, details = False)
logging.info('FSTA.main.py start')

import config

m = config.get_installation()

m.run()
