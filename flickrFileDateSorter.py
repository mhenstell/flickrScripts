import redis
import sys, os

r = redis.StrictRedis(host='localhost', port=6379, db=0)

date = sys.argv[1]

if __name__ == "__main__":
	
	os.chdir(date)
	files = os.listdir(os.getcwd())
		
	pics = [f for f in files if os.path.splitext(f)[1] == ".jpg"]
	
	picMap = {}
	
	for pic in pics:
		id = pic.split("_")[0]
		picMap[id] = pic
	
	print "picMap length: " + str(len(picMap))
	
	length = r.llen("sortedIdsByDate:" + date)
	
	print "sortedIdsByDate:" + date + " length: " + str(length)
	
	for x in range(0, length):
		id = r.lindex("sortedIdsByDate:" + date, x)
		
		try:
			print "Renaming %s to %s" % (picMap[id], str(x) + ".jpg")
			os.rename(picMap[id], str(x) + "-" + id + ".jpg")
		except KeyError, e:
			print "Couldn't find file for " + id + ": " + str(e)
		
	