import redis, json

r = redis.StrictRedis(host='localhost', port=6379, db=0)

keys = r.keys("dateTaken:*")
for key in keys:
	r.delete(key)

print "dateTaken keys flushed"

ids = r.smembers("picSet")

bestDate = ""
bestDateNum = 0

for id in ids:

	info = r.get(id + ":info")
	exif = r.get(id + ":exif")
	
	if info is None or exif is None: continue
	
	info = json.loads(info)
	exif = json.loads(exif)
	
	try:
		dateTakenInfo= info["photo"]["dates"]["taken"]
	except:
		print "Error getting info: " + str(info)
		continue
	
	dateTaken = dateTakenInfo.split(" ")[0]
	#timeTaken = dateTakenInfo.split(" ")[1]
	
	r.set(id + ":dateTimeTaken", dateTakenInfo)
	
	#dateTakenSplit = dateTaken.split("-")
	#yearTaken = dateTakenSplit[0]
	#monthTaken = dateTakenSplit[1]
	#dayTaken = dateTakenSplit[2]
	
	num = r.incr("dateTaken:" + dateTaken)
	
	r.sadd("dateTakenIDs:" + dateTaken, id)
	
	if num > bestDateNum: 
		bestDate = dateTaken
		bestDateNum = num
	
	print "Date Taken: " + dateTaken + " - " + str(num)

print "Best Date: " + bestDate + " - " + r.get("dateTaken:" + bestDate)