import os
import sys
import redis
import operator
import json
import optparse
import flickrapi
import time
import threading
from Queue import Queue

try:
	import flickrcredentials
except:
	"Could not find flickr credentials file"
	sys.exit(1)

class InfoGetter(threading.Thread):
	def __init__(self, id):
		print "Init " + str(id)
		self.id = id
		threading.Thread.__init__(self)

def _populateData():
	
	def getter(q, ids):
		for pic in infoQueue:
			thread = InfoGetter(id)
			thread.start()
			q.put(thread, True)
	
	infoQueue = r.smembers("infoQueue")
	
	q = Queue(3)
	
	threads = threading.Thread(target=getter, args=(q, infoQueue))
	threads.start()
	threads.join()

def _searchFlickr(mindate, maxdate, woe_id):
	
	#for photo in flickr.walk(min_taken_date=minDate, max_taken_date=maxDate, has_geo=True, woe_id=woe_id):
	#search = flickr.photos_search(api_key=flickrcredentials.api_key, min_taken_date=mindate, max_taken_date=maxdate, has_geo=True, woe_id=woe_id, format='json').replace("jsonFlickrApi(", "")[0:-1]
	#search = json.loads(search)
	
	currentPage = 1
	totalPages = 0
	
	while True:
		search = flickr.photos_search(api_key=flickrcredentials.api_key, min_taken_date=mindate, max_taken_date=maxdate, has_geo=True, woe_id=woe_id, page=currentPage, format='json').replace("jsonFlickrApi(", "")[0:-1]
		search = json.loads(search)
		
		totalPages = search["photos"]["pages"]
		photos = search["photos"]["photo"]
		
		for photo in photos:
			id = photo["id"]
			
			#Add photo to master picture set
			ret = r.sadd("picSet", id)
			if ret == 1: r.sadd("infoQueue", id)

		currentPage += 1
		if currentPage > totalPages: break

		time.sleep(1)
		

if __name__ == "__main__":
	
	parser = optparse.OptionParser()
	parser.add_option('--min', action="store")
	parser.add_option('--max', action="store")
	parser.add_option('-d', '--download', default=False)
	parser.add_option('-w', '--woe-id', action="store", dest="woe", default="2459115")
	
	options,args = parser.parse_args()
	
	flickr = flickrapi.FlickrAPI(flickrcredentials.api_key, flickrcredentials.api_secret)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	#_searchFlickr(options.min, options.max, options.woe)
	_populateData()