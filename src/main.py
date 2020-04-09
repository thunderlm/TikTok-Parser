import utils
import argparse

#TODO: What if tags shows no results (for example mispell)? -> wait error
#      Is it better maybe to write in a doc the basic settings?
#      Give possibility to continue scraping of infinitly?
#      Change driver randomly?
#      Maybe save (intermediate) results?
#	   Start now with "metrics" function? (Ma se non le sappiamo ancora..)
#	   Sistemare i verbose

def main(tagNames, prams, verbose=False):

	#Initialize 
	stats_authors = dict()
	
	# Get current location
	path = utils.getPath()

	# Get selenium driver
	driver = utils.getDriver(path)
	
	#Get all the tags:
	tagNameList = utils.get_names_tags(tagNames)

	for tagName in tagNameList:
	
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

	# Close drivers
	driver.close()
	driver.quit() 







if __name__ == "__main__":

	# Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--tag', type=str, required=True)
	parser.add_argument('--minNFollowers', type=int, required=True)
	parser.add_argument('--maxNFollowers', type=int, required=True)
	parser.add_argument('--minNLikes', type=int, required=True)
	parser.add_argument('--maxNLikes', type=int, required=True)
	args = parser.parse_args()
	
	# Run main
	params = args.minNFollowers, args.maxNFollowers, args.minNLikes, args.maxNLikes
	main(args.tag, params)

