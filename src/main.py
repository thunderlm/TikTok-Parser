import utils
import traceback
import selenium_functions as sf

#TODO: What if tags shows no results (for example mispell)? -> wait error
#      Change driver randomly?
#      Maybe save (intermediate) results?
#	   Sistemare i verbose

def main(verbose=False):

	try:
		#Initialize 
		stats_authors = dict()
		
		# Get current location
		path = utils.getPath()
		params = utils.loadJson(path + "/docs/parameters.json")

		# Get selenium driver
		driver = sf.getDriver(path)

		# Iterate over tags
		for tagName in params["tags"]:
			print("--------------- Starting tag "+tagName+ " ---------------")
			# Get tag URL
			driver.get('https://www.tiktok.com/tag/' + tagName)
			
			# Scroll in tags
			login_form, driver = sf.scrollPage(driver, scope="tag", maxNScrolls=50)
		    
		    #Get authors names:
			authors_list = sf.get_authors(login_form, driver)
			print("--------------- Found ",len(authors_list),"users: ---------------")
			#Extract statistics from each author:		
			stats_authors = sf.get_stats_author(driver, authors_list, params, stats_authors, useTikster=True)

		#Compute metrics for each author:
		metrics_author = sf.compute_metrics(stats_authors)

		#print(metrics_author)

	except Exception as e:
		traceback.print_exc()

	finally:
		# Check whether driver has been initialized yet
		try:
			driver
		except NameError:
			driver = None

		# Always close drivers
		if not driver is None:
			driver.close()
			driver.quit()
			print("Driver closed")



if __name__ == "__main__":
	main()