import utils
import traceback


#TODO: What if tags shows no results (for example mispell)? -> wait error
#      Is it better maybe to write in a doc the basic settings?
#      Give possibility to continue scraping of infinitly?
#      Change driver randomly?
#      Maybe save (intermediate) results?
#	   Start now with "metrics" function? (Ma se non le sappiamo ancora..)
#	   Sistemare i verbose

def main(verbose=False):

	try:
		#Initialize 
		stats_authors = dict()
		
		# Get current location
		path = utils.getPath()
		params = utils.loadJson(path + "/docs/parameters.json")

		# Get selenium driver
		driver = utils.getDriver(path)

		# Iterate over tags
		for tagName in params["tags"]:
			# Get tag URL
			driver.get('https://www.tiktok.com/tag/' + tagName)
			
			# Scroll in tags
			login_form = utils.scrollPage(driver, scope="tag", n =1)
		    
		    #Get authors names:
			authors_list = utils.get_authors(login_form)
		
			#Extract statistics from each author:		
			stats_authors = utils.get_stats_author(driver, authors_list, params, stats_authors)


		# Scroll videos
		'''profileVideos = utils.scrollPage(driver, scope="author")

		# Get video links
		linkVideos = utils.getLinkVideos(profileVideos)
		print(linkVideos)'''

		print(stats_authors)

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