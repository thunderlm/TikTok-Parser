import utils
import argparse



def main(tagName):

	# Get current location
	path = utils.getPath()

	# Get selenium driver
	tagDriver = utils.getDriver(path)

	# Get tag URL
	tagDriver.get('https://www.tiktok.com/tag/' + tagName)

	# Scroll in tags
	login_form = utils.scrollPage(tagDriver, scope="tag")
    
    #Get authors names:
	authors_list = utils.get_authors(login_form, verbose = True)





	# Close drivers
	tagDriver.close()








if __name__ == "__main__":

	# Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--tag', type=str, required=True)
	args = parser.parse_args()
	
	# Run main
	main(args.tag)

