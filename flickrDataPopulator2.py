import os
import sys
import redis
import json
from multiprocessing import Pool

class FlickrDataDownloader:

	children = {}
	jobs = []					# current list of queued jobs

	def __init__(self, flickrInstance, redisInstance, workers=8):
		self.flickrInstance = flickrInstance
		self.redisInstance = redisInstance
		self.workers = workers

	def run(self):

		ids = redisInstance.smembers("infoQueue")

		pool = Pool(processes = self.workers)
		print pool.map(retrieveDataForID, ids)

	def retrieveDataForID(self, id, flickrInstance, redisInstance):

		print "Retriving data for %s" % id

		exif = flickrInstance.photos_getExif(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
		info = flickrInstance.photos_getInfo(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]

		redisInstance.set(id + ":info", info)
		redisInstance.set(id + ":exif", exif)
		redisInstance.srem("infoQueue", id)

		return True
	
	
	
	
	