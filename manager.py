#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
import configparser
from worker import Worker
import time
import schedule

import logging

class Manager(Thread):
	def __init__(self, config_file, info_file):
		Thread.__init__(self)
		self.name = 'manager'
		
		#logger config
		logger = logging.getLogger(self.name)
		hdlr = logging.FileHandler('logs/' + self.name + '.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr) 
		logger.setLevel(logging.INFO)
		self.logger = logger
		
		#config
		config = configparser.ConfigParser()
		config.read(config_file)
		
		#usersinfo
		info = configparser.ConfigParser()
		info.read(info_file)
			
		self.threads = set()
		
		for section in info.sections():
			login = info.get(section, 'Login')
			password = info.get(section, 'Password')
			tags = info.get(section, 'Tags')
			tag_list = [x.strip() for x in tags.split(',')]
			
			tag_depth = int(info.get(section, 'TagDepth'))
			like_depth = int(info.get(section, 'LikeDepth'))
			
			#logging.info("%s:\n user = %s \n tags = %s \n tag_depth = %s \n like_depth = %s " % (section, login, tags, tag_depth, like_depth))
			
			worker = Worker(section, info_file)
			#worker.setDaemon(True)
			
			self.threads.add(worker)
	
		
		
		self.active = True
	
	#def start(self):
	#	logger = self.logger
	#	logger.info('Start...')
	#	self.active = True
	#	#for thread in self.threads:
	#	#	thread.start()
	#		
	def run(self):
		logger = self.logger
		
		self.set_operation_type_for_all('like_and_follow')
		#self.set_operation_type_for_all('unfollow')
		self.start_all_workers()
		
		
		schedule.every(60).seconds.do(self.log_info)
		schedule.every(60).seconds.do(self.check_all_workers)
		
		schedule.every().day.at("10:00").do(self.set_operation_type_for_all, 'like_and_follow')
		schedule.every().day.at("22:30").do(self.set_operation_type_for_all, 'unfollow')
		
		schedule.every().day.at("04:30").do(self.pause_all_workers)
		schedule.every().day.at("23:59").do(self.clear_all_workers)
		schedule.every().day.at("11:00").do(self.resume_all_workers)
		

		while self.active:
			schedule.run_pending()
			time.sleep(1)		
		#schedule.every().hour.do(job)
		

		#		
		#while self.active:
		#	time.sleep(30)
		#	for thread in self.threads:
		#		logger.info('%s - likes: %s, follows: %s.' % (thread.name, thread.like_count, thread.follow_count))
		#		if thread.follow_count >= 500:
		#			thread.pause()
				
			
	def stop(self):
		logger = self.logger
		logger.info('Stop...')
		self.stop_all_workers()
		self.active = False
			
	def start_all_workers(self):
		for thread in self.threads:
			thread.start()
			
	def stop_all_workers(self):
		for thread in self.threads:
			thread.stop()	
			
	def pause_all_workers(self):
		for thread in self.threads:
			thread.pause()	
			
	def resume_all_workers(self):
		for thread in self.threads:
			thread.resume()
			
	def clear_all_workers(self):
		for thread in self.threads:
			thread.like_count = 0
			thread.follow_count = 0
			thread.unfollow_count = 0
			
	def check_all_workers(self):
		for thread in self.threads:
			if thread.follow_count >= 500:
				thread.pause()
			
	def set_operation_type_for_all(self, operation):
		for thread in self.threads:
			thread.set_operation_type(operation)

	def job(self):
		print("I'm working...")
		
	def log_info(self):
		for thread in self.threads:
			self.logger.info('%s - likes: %s, follows: %s, unfollows: %s.' % (thread.name, thread.like_count, thread.follow_count, thread.unfollow_count))

