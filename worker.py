#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
from selenium import webdriver
import time
import random
import configparser
from constants import *
import traceback

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

import logging

class Worker(Thread):
	def __init__(self, name, info_file):
		Thread.__init__(self)
		
		#logger config
		logger = logging.getLogger(name)
		hdlr = logging.FileHandler(name + '.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr) 
		logger.setLevel(logging.INFO)
		self.logger = logger
		
		self.name = name
		self.info_file = info_file

		self.like_count = 0
		self.follow_count = 0
		self.unfollow_count = 0
		
		self.operation = 'like_and_follow'
		self.active = True
		
	def run(self):
		logger = self.logger
				
		while self.active:
			name = self.name
			info_file = self.info_file
			
			#read config
			config = configparser.ConfigParser()
			config.read(info_file)
			login = config.get(name, 'Login')
			password = config.get(name, 'Password')
			tags = config.get(name, 'Tags')
			tag_list = [x.strip() for x in tags.split(',')]
			tag_depth = int(config.get(name, 'TagDepth'))
			like_depth = int(config.get(name, 'LikeDepth'))
			logger.info("Config %s:\n user = %s \n tags = %s \n tag_depth = %s \n like_depth = %s " % (name, login, tags, tag_depth, like_depth))
			
			# init browser
			
			#Chrome
			options = webdriver.chrome.options.Options()
			#options.add_argument("--disable-extensions") # optional and off-topic, but it conveniently prevents the popup 'Disable developer mode extensions' 
			#browser = webdriver.Chrome(chrome_options=options)
			
			#Firefox
			#browser = webdriver.Firefox()

			#PhantomJS
			#browser = webdriver.PhantomJS()
			
			browser.set_window_position(0, 0)
			browser.set_window_size(1024, 700)
			browser.set_page_load_timeout(30)
			
			#actions
			try:
				#login
				self.log_to_instagram(browser, login, password)
				
				logger.info('Operation type: %s' % (self.operation))
				
				if self.operation == 'like_and_follow':
					#like all and follow
					for tag in tag_list:
						nicknames = self.like_new_photos_by_tag(browser, tag, tag_depth)
						for nickname in nicknames:
							wait_interval()
							self.like_by_nickname(browser, nickname, like_depth)
				elif self.operation == 'unfollow':
					self.unfollow(browser, login)
					
			except TimeoutException:
				logger.error('Catched Timeout Exception. (%s)' % (traceback.format_exc()))
			except NoSuchElementException:
				logger.error('Unable to find element. (%s)' % (traceback.format_exc()))
			except Exception:
				logger.error('Other exception. (%s)' % (traceback.format_exc()))
			else:
				logger.info('Finished successfully.')
			finally:			
				#close browser
				browser.stop_client()
				browser.close();
				browser.quit();
				logger.info('Browser closed.')
				#wait
		
	def stop(self):
		logger = self.logger
		logger.info('Stop...')
		self.active = False
	
	def pause(self):
		logger = self.logger
		logger.info('Pause...')
		self.active = False
	
	def resume(self):
		logger = self.logger
		logger.info('Resume...')
		self.active = True
	
	def set_operation_type(self, operation):
		self.operation = operation
	
	def log_to_instagram(self, browser, login, password):
		logger = self.logger
		logger.info( u'Login...' )
		
		browser.get('https://www.instagram.com/accounts/login/')
		assert "Instagram" in browser.title
			
		wait_interval()
		log_text = browser.find_element_by_name("username")
		log_text.send_keys(login)
		pass_text = browser.find_element_by_name("password")
		pass_text.send_keys(password)
		wait_interval()

		button = browser.find_element_by_xpath(XPATH_LOG_BTN)

		button.click()
		wait_interval()
		return True
		

		

	def like_new_photos_by_tag(self, browser, tag, tag_depth):
		logger = self.logger
		nicknames = set()
		
		logger.info( u'Finding photos with tag: ' + tag )
		wait_interval()
		browser.get('https://instagram.com/explore/tags/' + tag);
		wait_interval()
		browser.save_screenshot('screen.png')
		
		first_photo = browser.find_element_by_xpath(XPATH_NEW_FIRST_PHOTO)
			
		wait_interval()
		first_photo.click()
		wait_interval()
		
		for i in range(0, tag_depth):
			username = browser.find_element_by_xpath(XPATH_USERNAME).get_attribute('title')

			nicknames.add(username)
			logger.info( u'Photo by username: ' + username )
			
			## check if liked and like
			#like_btn = browser.find_element_by_xpath(XPATH_LIKE_BTN)
			#
			#if like_btn.get_attribute('class').find('coreSpriteHeartOpen') > 0: 
			#	#like_btn.click()
			#	#self.like_count += 1
			#	#logger.info(u'Like!')
			#	pass
						
			# check if next photo available and click next
			if i != tag_depth - 1:
				try:
					next_btn = browser.find_element_by_xpath(XPATH_NEXT_BTN)
				except NoSuchElementException:
					logger.info(u'No next photo available.')
					continue
				else:
					next_btn.click()
					logger.info(u'Next')
			
			wait_interval()
				
		return nicknames
		

	def like_by_nickname(self, browser, nickname, like_depth):
			logger = self.logger
			#print "Like: " + nickname
			logger.info( u'Liking for nickname: ' + nickname)
			browser.get('https://instagram.com/' + nickname);
			wait_interval()
			
			
			first_photo = browser.find_element_by_xpath(XPATH_FIRST_PHOTO_ON_ACCOUNT)
			
			wait_interval()
			first_photo.click()		
			wait_interval()
			
			for i in range(0, like_depth):
				# check if liked and like
				like_btn = browser.find_element_by_xpath(XPATH_LIKE_ON_ACCOUNT_BTN)
					
				if like_btn.get_attribute('class').find('coreSpriteHeartOpen') > 0: 
					like_btn.click()
					self.like_count += 1
					logger.info(u'Like!')
				elif like_btn.get_attribute('class').find('coreSpriteHeartFull') > 0: 
					logger.info(u'Already liked')
							
				# check if next photo available and click next
				if i != like_depth - 1:
					try:
						if i == 0:
							next_btn = browser.find_element_by_xpath(XPATH_NEXT_FIRST_ON_ACCOUNT_BTN)
						else:
							next_btn = browser.find_element_by_xpath(XPATH_NEXT_ON_ACCOUNT_BTN)
					except NoSuchElementException:
						logger.info(u'No next photo available.')
						continue
					else:
						next_btn.click()
						logger.info(u'Next')
				else:
					try:
						follow_btn = browser.find_element_by_xpath(XPATH_FOLLOW_ON_PHOTO_ON_ACCOUNT_BTN)
					except NoSuchElementException:
						logger.info("Unable to find follow button")
					else:
						if follow_btn.text == u'Подписаться':
							follow_btn.click()
							self.follow_count += 1
							logger.info( u'Follow %s!' % (nickname))
						elif follow_btn.text in (u'Подписки', u'Запрос отправлен' ):
							logger.info( u'User %s already followed.' % (nickname))
						else:
							logger.info( u'Unknown status of following (%s).' % (nickname))
						
				wait_interval()
				
	def unfollow(self, browser, login):
		logger = self.logger
		
		logger.info( u'Unfollowing...' )
		browser.get('https://www.instagram.com/%s/' % login)
		wait_interval()			
			
		followers_btn = browser.find_element_by_xpath(XPATH_FOLLOWERS_BTN)
		
		followers_btn.click()
		wait_interval()
		
		for i in range(random.randint(2, 6), 40):
			
			unfollow_btn = browser.find_element_by_xpath(XPATH_UNFOLLOW_BTN.replace("button_number", str(i)))
			
						
			browser.execute_script("return arguments[0].scrollIntoView();", unfollow_btn)
			
			unfollow_btn.click()
			self.unfollow_count += 1
			logger.info( 'Unfollow!')
			wait_interval()
			
		return True
				
def wait_interval():
	time.sleep(random.uniform(1.1, 2.4))