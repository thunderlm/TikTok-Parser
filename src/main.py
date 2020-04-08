import utils
import argparse



def main(tagName):

	# Get current location
	path = utils.getPath()

	# Get selenium driver
	tagDriver = utils.getDriver(path)

	# Get tag URL
	tagDriver.get('https://www.tiktok.com/tag/' + tagName)

	# Scroll
	#utils.scrollPage(tagDriver)





	# Close drivers
	tagDriver.close()








if __name__ == "__main__":

	# Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--tag', type=str, required=True)
	args = parser.parse_args()
	
	# Run main
	main(args.tag)

