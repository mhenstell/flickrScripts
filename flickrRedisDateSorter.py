import redis
import sys

r = redis.StrictRedis(host='localhost', port=6379, db=0)

if __name__ == "__main__":

	delKeys = r.keys("sortedIdsByDate:*")
	for key in delKeys:
		r.delete(key)
		
	keys = r.keys("*:dateTimeTaken")
	
	ids = []
	
	for key in keys:
		id = key.split(":")[0]
		ids.append(id)
	
	idMap = {}
	
	for id in ids:
		idMap[id] = r.get(id + ":dateTimeTaken")
	
	sortedIdMap = sorted(idMap, key=idMap.__getitem__, reverse=True)
	
	for id in sortedIdMap:
		dateTime = idMap[id]
		date = dateTime.split(" ")[0]
	
		r.lpush("sortedIdsByDate:" + date, id)
		print "sortedIdsByDate:" + date + " - " + str(r.lrange("sortedIdsByDate:" + date, 0, -1))