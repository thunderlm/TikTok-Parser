import os
import json
import pandas

def getPath():
	path = os.getcwd()
	# Run script main from main folder, NOT FROM src
	assert(path.split("/")[-1] == "TikTok-Parser")
	return path

def loadJson(path):
	with open(path) as json_file:
		return json.load(json_file)

def extract_author_from_link(link_video):
	if "@" not in link_video:
		print("WARNING: Could not find @ in link, hence no username")
		return None
	cropped_link = link_video[link_video.find("@")+1:]
	author_name = cropped_link[:cropped_link.find("/")]
	return author_name

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
		elif numbers[i][-1] == "B":
			numbers[i] = int(float(numbers[i][:-1]) * 1e9)
		else:
			numbers[i] = int(numbers[i])

	return numbers

def save_metrics(stats_authors, path_save="docs/result_metrics.json"):
	#Save results in json file (for future handling)
	with open(path_save, 'w') as f:
		json.dump(stats_authors, f)

	#Save results in xml file (for visualization)
	data = pandas.read_json(path_save)
	data_t = data.transpose()
	data_t.to_excel(path_save.replace("json","xlsx"))
	print("Results saved in", path_save.replace("json","xlsx"))
	
def divide(a,b):
	exact_result = float(a)/(b+1e-5)	
	#round to two decimals:
	r =  float("{:.2f}".format(exact_result))
	return r 
	
	
	
	
	
	


