import flickrapi
import redis
import json
import time



if __name__ == "__main__":
	
	flickr = flickrapi.FlickrAPI(api_key, api_secret)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	while True:
		time.sleep(1)
		id = r.spop("infoQueue")
		if (id is None): continue
		
		exists = r.exists(id + ":info")
		if (exists):
			print "\tSkipping " + id
			continue
		
		print "Retriving data for %s" % (id)
		
		exif = flickr.photos_getExif(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
		info = flickr.photos_getInfo(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
		
		r.set(id + ":info", info)
		r.set(id + ":exif", exif)
		
		