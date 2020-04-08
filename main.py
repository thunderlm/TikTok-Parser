#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 21:21:05 2020

@author: andrea
"""
import time 
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options


profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", "Naverbot")
driver = webdriver.Firefox(profile,executable_path=r'/home/andrea/Documents/WEB-CRAWLER/geckodriver-v0.26.0-linux64/geckodriver')

#driver.get('https://www.tiktok.com/tag/magic')
driver.get('https://www.tiktok.com/@thecardguy/')

while True:
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 1000000)") 
