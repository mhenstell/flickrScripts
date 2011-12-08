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

class InfoGetter(threading.Thread): #Class 
	
	def __init__(self, picID):
		self.picID = picID
		self.result = False
		threading.Thread.__init__(self)
	
	def run(self):
		exists = r.exists(self.picID + ":info")
		if (exists):
			r.srem("infoQueue", self.picID)
			self.result = True
			return
		
		try:
			exif = flickr.photos_getExif(photo_id=self.picID, format="json").replace("jsonFlickrApi(", "")[0:-1]
			info = flickr.photos_getInfo(photo_id=self.picID, format="json").replace("jsonFlickrApi(", "")[0:-1]
		
		except:
			self.result = False
			return
			
		r.set(self.picID + ":info", info)
		r.set(self.picID + ":exif", exif)
	
		r.srem("infoQueue", self.picID)
			
		self.result = True
		
	def get_result(self):
		return self.result

def _populateData(): #Uses a series of threads to query Flickr to populate redis with EXIF data
	
	def producer(q, ids):
		counter = 1
		for pic in infoQueue:
			print "Retriving Data for Picture %s / %s" % (counter, len(infoQueue))
			thread = InfoGetter(pic)
			thread.start()
			q.put(thread, True)
			counter += 1
	
	finished = []
	
	def consumer(q, total_ids):
		while len(finished) < total_ids:
			thread = q.get(True)
			thread.join()
			
			result = thread.get_result()
			if result: finished.append(result)
			
	infoQueue = r.smembers("infoQueue")
	if len(infoQueue) == 0:
		print "No pictures queued for data population"
		return
	
	q = Queue(8)
	
	prod_thread = threading.Thread(target=producer, args=(q, infoQueue))
	cons_thread = threading.Thread(target=consumer, args=(q, len(infoQueue)))
	
	prod_thread.start()
	cons_thread.start()
	prod_thread.join()
	cons_thread.join()

def _searchFlickr(mindate, maxdate, woe_id):
	
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

def _dateTabulator():
	
	print "Flushing dateTaken keys"
	keys = r.keys("dateTaken:*")
	for key in keys:
		r.delete(key)
	
	print "Retabulating dateTaken keys"
	ids = r.smembers("picSet")
	counter = 0
	
	for id in ids:
		counter += 1
		if counter % 100 == 0:
			print "Tabulating date data for picture %s/%s" % (counter, len(ids))
			
		info = r.get(id + ":info")
		exif = r.get(id + ":exif")
		
		if info is None or exif is None: continue
		
		info = json.loads(info)
		exif = json.loads(exif)
		
		try:
			dateTakenInfo = info["photo"]["dates"]["taken"]
		except:
			print "Error getting info: " + str(info)
			continue
		
		dateTaken = dateTakenInfo.split(" ")[0]
		num = r.incr("dateTaken:" + dateTaken)
		
		r.set(id + ":dateTimeTaken", dateTakenInfo)
		r.sadd("dateTakenIDs:" + dateTaken, id)

def _redisDateSorter():
	print "Flushing sortedIDSbyDate keys"
	
	delKeys = r.keys("sortedIDSbyDate:*")
	for key in delKeys:
		r.delete(key)
	
	
		
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
	#_populateData()
	#_dateTabulator()