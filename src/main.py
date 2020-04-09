import utils
import argparse



def main(tagName, minNFollowers, maxNFollowers, minNLikes, maxNLikes):

	# Statistics
	allStats = dict()

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

	for authorName in authors_list:
		# Request author page
		driver.get('https://www.tiktok.com/@' + authorName)

		# Get profile numbers like followers, following, N likes
		profileNumbers = driver.find_elements_by_class_name("number")
		assert(len(profileNumbers) == 3)

		# Convert stat strings to number and save in variables
		numbers = utils.convertStatsToNumber([element.text for element in profileNumbers])
		numFollowing = numbers[0]
		numFollowers = numbers[1]
		numLikes = numbers[2]

		# Skip if not microinfluencer
		if numFollowers < minNFollowers or numFollowers > maxNFollowers or numLikes < minNLikes or numLikes > maxNLikes:
			continue

		# Add profile to statistics
		if not authorName in allStats:
			allStats[authorName] = dict()
			allStats[authorName]["Following"] = numFollowing
			allStats[authorName]["Followers"] = numFollowers
			allStats[authorName]["NLikes"] = numLikes


		# Scroll videos
		'''profileVideos = utils.scrollPage(driver, scope="author")

		# Get video links
		linkVideos = utils.getLinkVideos(profileVideos)
		print(linkVideos)'''



	print(allStats)

	# Close drivers
	driver.close()








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

