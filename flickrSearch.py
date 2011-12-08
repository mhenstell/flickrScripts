import flickrapi
import redis
import sys


minDate = sys.argv[1]
maxDate = sys.argv[2]

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