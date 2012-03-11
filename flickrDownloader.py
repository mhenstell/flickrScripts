import os
import sys
import redis
import json



class FlickrDownloader:

	children = {}
	jobs = []					# current list of queued jobs
	
	# Default wget options to use for downloading each URL
	wget = ["wget", "-q", "-nd", "-np", "-c", "-r"]
	
	def __init__(self, redisInstance, workers=8):
		self.redisInstance = redisInstance
		self.maxjobs = workers

	# Spawn a new child from jobs[] and record it in children{} using
	# its PID as a key.
	def spawn(self,cmd, *args):
		argv = [cmd] + list(args)
		pid = None
		try:
			pid = os.spawnlp(os.P_NOWAIT, cmd, *argv)
			self.children[pid] = {'pid': pid, 'cmd': argv}
		except Exception, inst:
			print "'%s': %s" % ("\x20".join(argv), str(inst))
		print "spawned pid %d of nproc=%d njobs=%d for '%s'" % \
			(pid, len(self.children), len(self.jobs), "\x20".join(argv))
		return pid

	def run(self, date):
		
		dir = date

		try:
			os.mkdir(dir)
		except OSError:
			pass
			
		os.chdir(dir)

		urls = []
		
		ids = self.redisInstance.zrange("picturesbytimestamp:%s" % date, 0, -1, withscores=True)

		for idtuple in ids:
			
			id = idtuple[0]
			timestamp = int(idtuple[1])

			#try:
			info = self.redisInstance.hget("picturedata:%s" % date, id + ":info")
			info = json.loads(info)
			
			secret = info["photo"]["secret"]
			server = info["photo"]["server"]
			farm = info["photo"]["farm"]
			
			url = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm, server, id, secret)
			#urls.append(url)

			cmd = self.wget + ["-O", "%s.jpg" % timestamp, url]
			self.jobs.append(cmd)

			#except:
			#	print "Error getting picture info for %s" % id
			
		# Build a list of wget jobs, one for each URL in our input file(s).
		#for url in urls:
		#	if url is not None:
		#		cmd = self.wget + ["-O", "[url]
		#		self.jobs.append(cmd)
				
		print "%d wget jobs queued" % len(self.jobs)

		# Spawn at most maxjobs in parallel.
		while len(self.jobs) > 0 and len(self.children) < self.maxjobs:
			cmd = self.jobs[0]
			if self.spawn(*cmd):
				del self.jobs[0]
		print "%d jobs spawned" % len(self.children)

		# Watch for dying children and keep spawning new jobs while
		# we have them, in an effort to keep <= maxjobs children active.
		while len(self.jobs) > 0 or len(self.children):
			(pid, status) = os.wait()
			print "pid %d exited. status=%d, nproc=%d, njobs=%d, cmd=%s" % \
				(pid, status, len(self.children) - 1, len(self.jobs), \
				 "\x20".join(self.children[pid]['cmd']))
			del self.children[pid]
			if len(self.children) < self.maxjobs and len(self.jobs):
				cmd = self.jobs[0]
				if self.spawn(*cmd):
					del self.jobs[0]