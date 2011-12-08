#flickr doesn't let you put more than 18 photos in a gallery

import redis
import flickrapi
import sys, os
import json

date = sys.argv[1]

r = redis.StrictRedis(host='localhost', port=6379, db=0)


flickr = flickrapi.FlickrAPI(api_key, api_secret)

(token, frob) = flickr.get_token_part_one(perms='write')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

if __name__ == "__main__":

	resp = flickr.galleries_create(api_key = api_key, title = date + " In New York City", format="json").replace("jsonFlickrApi(", "")[0:-1]
	resp = json.loads(resp)
	
	galID = resp["gallery"]["id"]
	url = resp["gallery"]["url"]
	
	print "Gallery Created: " + galID, url
	
	ids = r.lrange("sortedIdsByDate:" + date, 0, -1)
	
	for id in ids:
		
		try:
			flickr.galleries_addPhoto(api_key = api_key, gallery_id = galID, photo_id = id)
			print "Added %s (%s) to %s" % (id, r.get(id + ":dateTimeTaken"), galID)
			
		except Exception, e:
		
			print "Error adding %s: %s" % (id, e)
			continue