import redis
import sys
import json

r = redis.StrictRedis(host='localhost', port=6379, db=0)

id = sys.argv[1]
if "-" in id:
	id = id.split("-")[1]
	
if __name__ == "__main__":
	 info = r.get(id + ":info")
	 info = json.loads(info)
	 
	 secret = info["photo"]["secret"]
	 server = info["photo"]["server"]
	 farm = info["photo"]["farm"]
	 
	 url = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm, server, id, secret)
	 
	 print url