import utils
import argparse



def main(tagName, minNFollowers, maxNFollowers, minNLikes, maxNLikes):

	# Get current location
	path = utils.getPath()

	# Get selenium driver
	driver = utils.getDriver(path)

	# Get tag URL
	driver.get('https://www.tiktok.com/tag/' + tagName)

	# Scroll in tags
	login_form = utils.scrollPage(driver, scope="tag")
    
    #Get authors names:
	authors_list = utils.get_authors(login_form)

	#Extract statistics from each author:		
	params = [minNFollowers, maxNFollowers, minNLikes, maxNLikes]
	stats_authors = utils.get_stats_author(driver, authors_list, params)


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
	main(args.tag, args.minNFollowers, args.maxNFollowers, args.minNLikes, args.maxNLikes)

