import os
import sys
import redis
import operator
import json

children = {}
maxjobs = 8					# maximum number of concurrent jobs
jobs = []					# current list of queued jobs

# Default wget options to use for downloading each URL
wget = ["wget", "-q", "-nd", "-np", "-c", "-r"]

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Spawn a new child from jobs[] and record it in children{} using
# its PID as a key.
def spawn(cmd, *args):
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

if __name__ == "__main__":
	
	dateTaken = sys.argv[1]
	
	try:
		os.mkdir(dateTaken)
	except OSError:
		pass
		
	os.chdir(dateTaken)
	
	ids = r.smembers("dateTakenIDs:" + dateTaken)
	
	urls = []
	
	for id in ids:
		info = r.get(id + ":info")
		info = json.loads(info)
		
		secret = info["photo"]["secret"]
		server = info["photo"]["server"]
		farm = info["photo"]["farm"]
		
		url = "http://farm%s.static.flickr.com/%s/%s_%s.jpg" % (farm, server, id, secret)
		
		urls.append(url)
		
	# Build a list of wget jobs, one for each URL in our input file(s).
	for url in urls:
		if url is not None:
			cmd = wget + [url]
			jobs.append(cmd)
			
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