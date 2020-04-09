import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

MAX_WAIT = 10

def get_names_tags(tagNames):
	#If it is a single word:
	if "," not in tagNames:
		return [tagNames]
	#If multiple words (separated by a comma)
	tagNameList = []
	while True:
		index = tagNames.find(",")		
		if index == -1:
			tagNameList.append(tagNames)
			return tagNameList

		tagNameList.append(tagNames[:index])
		tagNames = tagNames[index+1:]


def extract_author_from_link(link_video):
	cropped_link = link_video[link_video.find("@")+1:]
	author_name = cropped_link[:cropped_link.find("/")]
	return author_name


def getPath():
	path = os.getcwd()

	# Run script main from main folder, NOT FROM src
	assert(path.split("/")[-1] == "TikTok-Parser")
	
	return path


def getDriver(path):

	# Options
	options = Options()
	options.headless = True

	# Profile
	profile = webdriver.FirefoxProfile()
	profile.set_preference("general.useragent.override", "Naverbot")
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
		wait(driver, MAX_WAIT).until(lambda driver: len(driver.find_elements_by_xpath(fullXPath)) > n_videos-1)
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
		list_authors.append(author)
    #remove authors repetitions
	#list_authors = list(set(list_authors)) 
    
	if verbose == True: 
		for name_author in list_authors: print(name_author)
        
	return list_authors
    
def get_stats_author(driver, authors_list, params, allStats):
	
	minNFollowers, maxNFollowers, minNLikes, maxNLikes = params
	for authorName in authors_list:
		#If author already in allStats, increase TagCount and skip to next:
		if authorName in allStats:
			allStats[authorName]["TagCount"] += 1
			continue
		# Request author page
		driver.get('https://www.tiktok.com/@' + authorName)
		
		print("Fetching info of ",authorName)
		# Get profile numbers like followers, following, likes
		wait(driver, MAX_WAIT).until(lambda driver: len(driver.find_elements_by_class_name("number")) ==3)
		profileNumbers = driver.find_elements_by_class_name("number")
		assert(len(profileNumbers) == 3)

		# Convert stat strings to number and save in variables
		numbers = convertStatsToNumber([element.text for element in profileNumbers])
		numFollowing = numbers[0]
		numFollowers = numbers[1]
		numLikes = numbers[2]

		# Skip if not microinfluencer
		if numFollowers < minNFollowers or numFollowers > maxNFollowers or numLikes < minNLikes or numLikes > maxNLikes:
			continue

		# Add profile to statistics			
		allStats[authorName] = dict()
		allStats[authorName]["Following"] = numFollowing
		allStats[authorName]["Followers"] = numFollowers
		allStats[authorName]["NLikes"] = numLikes
		allStats[authorName]["TagCount"] = 1
		
		
	return allStats

def getLinkVideos(page):
	linkVideos = []
	for element in page:
		elementFiltered = element.find_elements_by_tag_name('a')
		assert(len(elementFiltered) == 1)
		linkVideos.append(elementFiltered[0].get_attribute('href'))

	assert(len(linkVideos) == len(list(set(linkVideos))))
	return linkVideos
		

def convertStatsToNumber(numbers):
	for i in range(len(numbers)):
		if numbers[i][-1] == "K":
			numbers[i] = int(float(numbers[i][:-1]) * 1e3)
		elif numbers[i][-1] == "M":
			numbers[i] = int(float(numbers[i][:-1]) * 1e6)
		else:
			numbers[i] = int(numbers[i])

	return numbers
