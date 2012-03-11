import os
import sys
import redis
import json
from multiprocessing import Pool

class FlickrDataDownloader:

	def __init__(self, flickrInstance, redisInstance, workers=4):
		self.flickrInstance = flickrInstance
		self.redisInstance = redisInstance
		self.workers = workers

	def run(self):

		ids = self.redisInstance.smembers("infoQueue")
		pool = Pool(processes = self.workers)
		print pool.map(self.retrieveDataForID, ids)

	def retrieveDataForID(self, id):

		print "Retriving data for %s" % id

		exif = self.flickrInstance.photos_getExif(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
		info = self.flickrInstance.photos_getInfo(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]

		self.redisInstance.set(id + ":info", info)
		self.redisInstance.set(id + ":exif", exif)
		self.redisInstance.srem("infoQueue", id)

		return True