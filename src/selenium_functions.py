#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 15:35:12 2020
@author: andrea
"""
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from utils import extract_author_from_link, convertStatsToNumber
import time 

#	Global variables
MAX_WAIT = 10


def getDriver(path):

	# Options
	options = Options()
	options.headless = True

	# Profile
	profile = webdriver.FirefoxProfile()
	
	# Write headers
	headers = {
		"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
		"referrer" : "https://google.com",
		"Upgrade-Insecure-Requests" : "1",
		"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
		"Accept-Encoding" : "gzip, deflate, br",
		"Accept-Language" : "en-US,en;q=0.9,es;q=0.8",
		'Pragma': 'no-cache'
	}
	headersKeys = list(headers.keys())
	profile.set_preference("modifyheaders.headers.count", len(headersKeys))
	for i in range(len(headersKeys)):
		profile.set_preference("modifyheaders.headers.name" + str(i), headersKeys[i])
		profile.set_preference("modifyheaders.headers.value" + str(i), headers[headersKeys[i]])

	driver = webdriver.Firefox(profile, options=options, executable_path=path + '/tools/geckodriver')
	
	return driver




#TODO: Handle errors in loading
def scrollPage(driver, scope, n=2):
	if scope == "tag":
		fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div/div"
	elif scope == "author":
		fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div/div"
	else:
		raise NameError('scope variable must be either tag or author')
        
	#Wait for first videos to load:
	wait(driver, MAX_WAIT).until(EC.presence_of_element_located((By.XPATH, fullXPath)))
	
	# Load ~30 new videos n times:
	for i in range(1,n+1):
		driver.execute_script("window.scrollTo(0, 1e6)")
		n_videos = ((i+1)*30)-15    
		#Current pezza because devo pensare come fare
		if scope == "tag":
			wait(driver, MAX_WAIT).until(lambda driver: len(driver.find_elements_by_xpath(fullXPath)) > n_videos-1)
		else:
			time.sleep(5)
		#time.sleep(1) #Are we sure we don't need this?
		login_form = driver.find_elements_by_xpath(fullXPath)
		print("current_length:",len(login_form),"min_length:",n_videos)


	login_form = driver.find_elements_by_xpath(fullXPath)
	return login_form


def get_authors(login_form, verbose=False):
	list_authors = []
	for element in login_form:
		#Currently the video link is in the element a
		element_filtered = element.find_elements_by_tag_name('a')
		#Make sure there is only one of such element
		if len(element_filtered) != 1: 
			raise ValueError('It was supposed to be only one element "a" ')
            
		link_video = element_filtered[0].get_attribute('href')
		author = extract_author_from_link(link_video)
		#Add to author list if there was no problems extracting the name:
		if author is not None:
			list_authors.append(author)

    #remove authors repetitions
	#list_authors = list(set(list_authors)) 
    
	if verbose == True: 
		for name_author in list_authors: print(name_author)
        
	return list_authors
    

def get_stats_author(driver, authors_list, params, allStats):
	
	for authorName in authors_list:
		#If author already in allStats, increase TagCount and skip to next:
		if authorName in allStats:
			allStats[authorName]["TagCount"] += 1
			continue
		# Request author page
		driver.get('https://www.tiktok.com/@' + authorName)
		
		print("Fetching info of ",authorName)
		# Get profile numbers like followers, following, likes
		try:
			wait(driver, MAX_WAIT).until(lambda driver: len(driver.find_elements_by_class_name("number")) ==3)
		except Exception as e:
			print("Exception : " + str(e) + " " + str(authorName))
			continue
			
		profileNumbers = driver.find_elements_by_class_name("number")
		assert(len(profileNumbers) == 3)

		# Convert stat strings to number and save in variables
		numbers = convertStatsToNumber([element.text for element in profileNumbers])
		numFollowing = numbers[0]
		numFollowers = numbers[1]
		numLikes = numbers[2]

		# Skip if not microinfluencer
		if numFollowers < params["minNFollowers"] or numFollowers > params["maxNFollowers"] or numLikes < params["minNLikes"] or numLikes > params["maxNLikes"]:
			allStats[authorName] = dict()
			allStats[authorName]["Candidate"] = False
			continue

		# Get views:
        #TODO: Should scroll till the end
		profileVideos = scrollPage(driver, scope="author", n=1) 
		numberVideos = len(profileVideos)
		viewsVideos = []
		for video in profileVideos:
			views_count = video.find_elements_by_tag_name('span')
			assert len(views_count) ==1
			string_number = views_count[0].text
			converted_number = convertStatsToNumber([string_number])[0]
			viewsVideos.append(converted_number)
			
		# Scroll videos
		'''
		# Get video links
		linkVideos = utils.getLinkVideos(profileVideos)
		print(linkVideos)'''
		

		# Add profile to statistics			
		allStats[authorName] = dict()
		allStats[authorName]["Candidate"] = True
		allStats[authorName]["Following"] = numFollowing
		allStats[authorName]["Followers"] = numFollowers
		allStats[authorName]["NLikes"] = numLikes
		allStats[authorName]["TagCount"] = 1
		allStats[authorName]["NVideos"] = numberVideos
		allStats[authorName]["ViewsSerie"] = viewsVideos
		
	return allStats

def compute_metrics(stats_authors):
	#Keep only the possible candidates:
	stats_authors = {s:stats_authors[s] for s in stats_authors if stats_authors[s]["Candidate"]}
	#Compute (more complex) metrics:
	for authorName, authorStats in stats_authors.items():
		stats_authors[authorName]["Following-Followers Ratio"] = float(authorStats["Following"])/authorStats["Followers"]
		stats_authors[authorName]["TotViews"]	 = sum(authorStats["ViewsSerie"])
		stats_authors[authorName]["Views-Followers Ratio"] = float(authorStats["Followers"])/authorStats["TotViews"]
		stats_authors[authorName]["AverageLikes"] = float(authorStats["NLikes"])/authorStats["NVideos"]
		stats_authors[authorName]["AverageViews"] = sum(authorStats["ViewsSerie"])/authorStats["NVideos"]
			
	return stats_authors
