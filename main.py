#!/usr/bin/env python
# -*- coding: utf-8 -*-
from manager import Manager
import time
import random

import logging

# Run following code when the program starts
if __name__ == '__main__':
	logging.basicConfig(format=u'%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
	
	global xpath_log_btn 
	xpath_log_btn = '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/span/button'

	manager = Manager('config.ini', 'info.ini')
	manager.setDaemon(True)
	manager.start()
	#time.sleep(3)
	#manager.stop()
	
	user_choice = input('Please click ENTER button to close application\n')
	if not user_choice:
		logging.info("Exit...")
		manager.stop()
		quit()
	
	try:
		while True:
			pass
	except KeyboardInterrupt:
		logging.info("exit...")
		manager.stop()
		
		
