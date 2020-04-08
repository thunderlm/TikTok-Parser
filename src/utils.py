import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver


def extract_author_from_link(link_video, verbose = False):
	cropped_link = link_video[link_video.find("@")+1:]
	author_name = cropped_link[:cropped_link.find("/")]
	if verbose == True: print(author_name) 
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


def scrollPage(driver):
	
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait as wait
	from selenium.webdriver.support import expected_conditions as EC
	fullXPath = "/html/body/div[1]/div/div[2]/div/div[1]/div/main/div/div"

	#Wait for first videos to load:
	wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, fullXPath)))
	# Load ~30 new videos n times:
	max_seconds_wait = 10
	n = 5
	for i in range(1,n+1):
		driver.execute_script("window.scrollTo(0, 1e6)")
		n_videos = ((i+1)*30)-15    
		wait(driver, max_seconds_wait).until(lambda driver: len(driver.find_elements_by_xpath(fullXPath)) > n_videos-1)
		#time.sleep(1) #Are we sure we don't need this?
		login_form = driver.find_elements_by_xpath(fullXPath)
		print("current_length:",len(login_form),"min_length:",n_videos)


	login_form = driver.find_elements_by_xpath(fullXPath)
	return login_form

def get_authors(login_form, verbose = False):
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
	list_authors = list(set(list_authors)) 
    
	if verbose == True: 
		for name_author in list_authors: print(name_author)
        
	return list_authors
    
