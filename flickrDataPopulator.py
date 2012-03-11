import redis
import json
from multiprocessing import Pool
import os
import flickrapi
import time

def retrieveDataForID(id):

	print "Retriving data for %s" % id

	flickrInstance =  flickrapi.FlickrAPI(os.environ['flickr_key'], os.environ['flickr_secret'])
	redisInstance = redis.StrictRedis(host=os.environ['redis_host'], port=int(os.environ['redis_port']), db=0)
	redisInstance.ping()

	exif = flickrInstance.photos_getExif(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
	info = flickrInstance.photos_getInfo(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]

	today = time.strftime("%Y-%m-%d", time.localtime())
	redisInstance.hmset("picturedata:%s" % today, {id + ":info": info, id + ":exif": exif})

class FlickrDataDownloader:

	def __init__(self, flickrInstance, redisInstance, workers=4):
		self.flickrInstance = flickrInstance
		self.redisInstance = redisInstance
		self.workers = workers

	def run(self):

		ids = self.redisInstance.smembers("picset")
		pool = Pool(processes = self.workers)
		pool.map(retrieveDataForID, ids)

