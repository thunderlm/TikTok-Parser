import os
from selenium.webdriver.firefox.options import Options
from selenium import webdriver



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
	# Load 30 new videos n times:
	max_seconds_wait = 10
	n = 5
	for i in range(1,n+1):
		driver.execute_script("window.scrollTo(0, 1e6)")
		n_videos = ((i+1)*30)-10    
		wait(driver, max_seconds_wait).until(lambda driver: len(driver.find_elements_by_xpath(fullXPath)) > n_videos-1)
		#time.sleep(1)
		login_form = driver.find_elements_by_xpath(fullXPath)
		print("current_length:",len(login_form),"min_length:",n_videos)


	login_form = driver.find_elements_by_xpath(fullXPath)
