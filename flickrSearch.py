import flickrapi
import redis
import sys
import json


class FlickrSearch:
	
	def __init__(self, minDate, maxDate, woe_id, flickrInstance, redisInstance):
		self.minDate = minDate
		self.maxDate = maxDate
		self.woe_id = woe_id
		self.redisInstance = redisInstance
		self.flickrInstance = flickrInstance

	def run(self):

		print "Performing Flickr search for photos in woe_id %s between %s and %s" % (self.woe_id, self.minDate, self.maxDate)

		currentPage = 1
		totalPages = 0
	
		while True:

			search = self.flickrInstance.photos_search(min_taken_date=self.minDate, max_taken_date=self.maxDate, has_geo=True, woe_id=self.woe_id, page=currentPage - 1, format='json').replace("jsonFlickrApi(", "")[0:-1]
			search = json.loads(search)
			
			totalPages = search["photos"]["pages"]
			photos = search["photos"]["photo"]

			print "\tPopulating Page %s of %s" % (currentPage, totalPages)
			
			for photo in photos:
				id = photo["id"]
				
				#Add photo to master picture set
				self.redisInstance.sadd("picset", id)

			currentPage += 1
			if currentPage > totalPages: break



if __name__ == "__main__":
	
	flickr = flickrapi.FlickrAPI(api_key, api_secret)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	counter = 1
	
	print "Retriving photos:"
	for photo in flickr.walk(min_taken_date=minDate, max_taken_date=maxDate, has_geo=True, woe_id="2459115"):
		id = photo.get("id")
		ret = r.sadd("picSet", id)
		if ret == 1: 
			print "\t" + str(counter) + ": " + id
			r.sadd("infoQueue", id)
			counter += 1