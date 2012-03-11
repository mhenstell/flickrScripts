import os
import sys
import redis
import json

class FlickrDataDownloader:

	children = {}
	jobs = []					# current list of queued jobs


	def __init__(self, flickrInstance, redisInstance, workers=8):
		self.flickrInstance = flickrInstance
		self.redisInstance = redisInstance
		self.maxjobs = workers

	# Spawn a new child from jobs[] and record it in children{} using
	# its PID as a key.
	def spawn(self, cmd, *args):
		argv = [cmd] + list(args)
		pid = None
		try:
			pid = os.spawnlp(os.P_NOWAIT, cmd, *argv)
			children[pid] = {'pid': pid, 'cmd': argv}
		except Exception, inst:
			print "'%s': %s" % ("\x20".join(argv), str(inst))
		print "spawned pid %d of nproc=%d njobs=%d for '%s'" % \
			(pid, len(children), len(jobs), "\x20".join(argv))
		return pid

	def run(self):

		ids = redisInstance.smembers("infoQueue")

		# Build a list of wget jobs, one for each URL in our input file(s).
		for id in ids:
			if id: jobs.append(['python', self.mainName, )
				
		print "%d wget jobs queued" % len(jobs)

		# Spawn at most maxjobs in parallel.
		while len(jobs) > 0 and len(children) < maxjobs:
			cmd = jobs[0]
			if spawn(*cmd):
				del jobs[0]
		print "%d jobs spawned" % len(children)

		# Watch for dying children and keep spawning new jobs while
		# we have them, in an effort to keep <= maxjobs children active.
		while len(jobs) > 0 or len(children):
			(pid, status) = os.wait()
			print "pid %d exited. status=%d, nproc=%d, njobs=%d, cmd=%s" % \
				(pid, status, len(children) - 1, len(jobs), \
				 "\x20".join(children[pid]['cmd']))
			del children[pid]
			if len(children) < maxjobs and len(jobs):
				cmd = jobs[0]
				if spawn(*cmd):
					del jobs[0]

	def retrieveDataForID(self, id):

		print "Retriving data for %s" % id

		exif = self.flickrInstance.photos_getExif(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]
		info = self.flickrInstance.photos_getInfo(photo_id=id, format="json").replace("jsonFlickrApi(", "")[0:-1]

		redisInstance.set(id + ":info", info)
		redisInstance.set(id + ":exif", exif)
		redisInstance.srem("infoQueue", id)
	
	
	
	
	