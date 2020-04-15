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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from utils import convertStatsToNumber, save_metrics, divide
import time 

#	Global variables
MAX_WAIT = 10

def scroll_shim(passed_in_driver, objectt):
        x = objectt.location['x']
        y = objectt.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (x,y)
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)

def extract_author_from_link(element, driver, link_video):
	if "@" not in link_video:
		print("WARNING: Could not find @ in link, retrying opening the video")

		#Scroll, hover and click on the video
		scroll_shim(driver, element)
		actions = ActionChains(driver)
		actions.move_to_element(element)
		actions.click()
		actions.perform()		
		
		#Stop a second for everything to load. Should be improved with a wait function?
		time.sleep(1) 

		#Get the information needed:
		fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div[2]/div/div[1]/div[2]"
		element_target = driver.find_elements_by_xpath(fullXPath)
		assert len(element_target) == 1
		element_filtered = element_target[0].find_elements_by_tag_name('a') 
		user_link = element_filtered[0].get_attribute('href') #Not sure why len>1
		
		#Press ESC to get out from video		
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
#TODO: Add mechanism if for any reason it still does not work		
		#Extract and return username:
		author_name = user_link[user_link.find("@")+1:]
		return author_name

	else:
		cropped_link = link_video[link_video.find("@")+1:]
		author_name = cropped_link[:cropped_link.find("/")]
		return author_name

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


def scrollPage(driver, scope, maxNScrolls=10):
	if scope == "tag":
		fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div/div"
	elif scope == "author":
		fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div/div"
	else:
		raise NameError('scope variable must be either tag or author')


	last_height = driver.execute_script("return document.body.scrollHeight")
	i = 0
	counter = 0 
	while i < maxNScrolls:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			counter +=1
			if counter>3:
				break
		else:
			counter = 0
		last_height = new_height
		i += 1
		 

	login_form = driver.find_elements_by_xpath(fullXPath)
	if scope == "author":
		if len(login_form) == 0:
			print("Mh non ha caricato nulla?",i)
	return login_form, driver


def get_authors(login_form, driver, verbose=False):
	list_authors = []
	for element in login_form:
		#Currently the video link is in the element a
		element_filtered = element.find_elements_by_tag_name('a')
		#Make sure there is only one of such element
		if len(element_filtered) != 1: 
			raise ValueError('It was supposed to be only one element "a" ')
            
		link_video = element_filtered[0].get_attribute('href')
		author = extract_author_from_link(element, driver, link_video)
		#Add to author list:
		list_authors.append(author)
    
	if verbose == True: 
		for name_author in list_authors: print(name_author)
        
	return list_authors
    

def get_stats_author(driver, authors_list, params, allStats, useTikster=True):
	
	for authorName in authors_list:
		#If author already in allStats, increase TagCount and skip to next:
		if authorName in allStats:
			if allStats[authorName]["Candidate"]:
				allStats[authorName]["TagCount"] += 1
			continue

		print("Fetching info of ",authorName)
		
		# Try to use Tikster to send less requests to TikTok
		# Skip if it is a special one, i.e. extracted from opening the video
		if useTikster and authorName[-1] != "?": 
			success, vals = get_tikster_author(driver, authorName)
			#If you managed to get it but didn't pass the tresholds, skip to next
			if success :
				numFollowing, numFollowers, numLikes = vals
				if numFollowers < params["minNFollowers"] or numFollowers > params["maxNFollowers"] or numLikes < params["minNLikes"] or numLikes > params["maxNLikes"]:
					allStats[authorName] = dict()
					allStats[authorName]["Candidate"] = False
					print("Skipped user thanks to Tikster")
					continue			
		
		# Request author page
		driver.get('https://www.tiktok.com/@' + authorName)
		
		# Get profile numbers like followers, following, likes
		try:
			wait(driver, MAX_WAIT).until(lambda driver: len(driver.find_elements_by_class_name("number")) ==3)
		except Exception as e:
			print("Exception : " + str(e) + " " + str(authorName))
			allStats[authorName] = dict()
			allStats[authorName]["Candidate"] = False			
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
		profileVideos, _ = scrollPage(driver, scope="author", maxNScrolls=20) 
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
		stats_authors[authorName]["Following-Followers Ratio"] = divide(authorStats["Following"],authorStats["Followers"])
		stats_authors[authorName]["TotViews"]	 = sum(authorStats["ViewsSerie"])
		stats_authors[authorName]["Views-Followers Ratio"] = divide(authorStats["TotViews"],authorStats["Followers"], round_result = False)
		stats_authors[authorName]["AverageLikes"] = divide(authorStats["NLikes"],authorStats["NVideos"])
		stats_authors[authorName]["AverageViews"] = divide(sum(authorStats["ViewsSerie"]),authorStats["NVideos"])
			
	save_metrics(stats_authors)		
	   
	return stats_authors

def get_tikster_author(driver, authorName):
	fullXPath = "/html/body/div/div/div[2]/div[1]/div[2]/div/div/div/div"	
	# Request author page
	driver.get('https://app.tikster.net/#/user/' + authorName)	
	try:
		#Wait to see if can load (usually takes more than TikTok)
		wait(driver, MAX_WAIT).until(EC.presence_of_element_located((By.XPATH, fullXPath+"[1]")))
		#If it loads in time, extract the stats:
		string = driver.find_elements_by_xpath(fullXPath+"[1]")[0].text
		numFollowing = int(string[:string.find("\n")].replace(",","") )

		string = driver.find_elements_by_xpath(fullXPath+"[2]")[0].text
		numFollowers = int(string[:string.find("\n")].replace(",",""))

		string = driver.find_elements_by_xpath(fullXPath+"[3]")[0].text
		numLikes = int(string[:string.find("\n")].replace(",",""))

		return True, [numFollowing, numFollowers, numLikes]
		
	except Exception as e:
		#If not load in time, exit and go as usual
		print("Tikster didn't load in time, falling back to TikTok")
		return False, None
