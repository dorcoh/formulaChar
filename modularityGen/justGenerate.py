import sys
import getopt
from os import listdir
import os
from threading import Timer
import subprocess
import random
import time

def kill_proc(proc, timeout):
  	timeout["value"] = True
  	proc.kill()

def runSolver(filename, timeout_sec):
	runstring = "./minisat {0}".format(filename)

	t1 = time.time()
	process = subprocess.Popen(runstring, shell=True, stdout=subprocess.PIPE)

	timeout = {"value": False}
	timer = Timer(timeout_sec, kill_proc, [process, timeout])
	timer.start()

	lines = []
	for line in process.stdout:
		lines.append(line)

	timer.cancel()
	if timeout["value"] == True:
		return "Timeout"

	matching = [s for s in lines if "SATISFIABLE" in s]
	solString = matching[0].split()[1]

	# remove comment in server
	#solString = solString.split()[1]

	process.wait()
	t2 = time.time()

	if solString == 'UNSATISFIABLE':
		return 0, None
	elif solString == 'SATISFIABLE':
		return 1, t2-t1

def runCachet(filename,timeout_sec):
	""" run Cachet model counter and return num of solutions """
	runstring = "./cachet {0}".format(filename)
	process = subprocess.Popen(runstring, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	timeout = {"value": False}
  	timer = Timer(timeout_sec, kill_proc, [process, timeout])
  	timer.start()

	lines = list()
	for line in process.stdout:
		lines.append(line)

	timer.cancel()
	if timeout["value"] == True:
		return None
	# handle cachet output
	#----------------------------------------
	matching = [s for s in lines if "Total Run Time" in s]
	if not matching:
		return None

	solString = matching[0]
	solString = solString.split()
	#----------------------------------------
	process.wait()
	# return runtime
	return int(float(solString[3]))

def runSTS(filename,timeout_sec):
	""" run sample tree model counter, return num of solutions """
	lines = list()
	runstring = "./STS {0}".format(filename)
	
	t1 = time.time()
	process = subprocess.Popen(runstring, shell=True, stdout=subprocess.PIPE)
	timeout = {"value": False}

  	timer = Timer(timeout_sec, kill_proc, [process, timeout])
  	timer.start()
  	"""
	for line in process.stdout:
		lines.append(line)
	"""
	process.wait()

	t2 = time.time()

	timer.cancel()
	if timeout["value"] == True:
		return None

	#matching = [s for s in lines if "Different" in s]

	#process.wait()
	return t2-t1

def runGenerator(n,m,c,q,filename,s):
	runstring = "./generator -n {0} -m {1} -c {2} -Q {3} -s {5} > {4}".format(n,m,c,q,filename,s)
	process = subprocess.Popen(runstring, shell=True, stdout=subprocess.PIPE)
	for line in process.stdout:
		print line
	process.wait()

def main(argv):
	variables = 600
	clauses = 2400
	communities = 5
	timeout=8000
	Q = 0.7

	# handle arguments
	try:
		opts, args = getopt.getopt(argv, "hv:c:t:m:q:")
	except getopt.GetoptError:
		print 'generate.py -v <InitVars> -c <InitClauses> -t <timeoutSec>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'generate.py -v <InitVars> -c <InitClauses> -t <timeoutSec> -m <communities> -q <Q ratio>'
			print '-v <InitVars> number of variables'
			print '-c <InitClauses> - number of variables of clauses'
			print '-t <timeoutSec> - Timeout in seconds for model counter (and solver)'
			print '-m <communities> - num of communities, default=0.5'
			print '-q <Q ratio> - Q ratio, default=0.7'
			sys.exit()
		elif opt in ("-v"):
			variables = int(arg)
		elif opt in ("-c"):
			clauses = int(arg)
		elif opt in ("-t"):
			timeout = int(arg)
		elif opt in ("-m"):
			communities = int(arg)
		elif opt in ("-q"):
			Q = float(arg)
	
	i = 0
	saved = 0
	maxi = 100
	# main loop for generating formulas
	while (saved<100):
		# init rand seed
		random.seed()
		# generate new filename
		filename = "vars-{0}-clauses-{1}-Q-{3}-id-{2}.cnf".format(variables,clauses,i,Q)
		print "Generating: {0}".format(filename)
		i+=1
		seed = random.randint(0,2**31-1)
		# generate formula
		runGenerator(variables,clauses,communities,Q,filename,seed)
		# if satisfiable
		sat, timeRun = runSolver(filename,int(timeout))
		if sat:
			print "SAT"
			print "Time for process: {0}".format(timeRun)
			print "Saved: {0}".format(filename)
			saved += 1
		# not satisfiable
		else:
			print "UNSAT"
			os.remove(filename)
			print "Removed: {0}".format(filename)


if __name__ == '__main__':
	main(sys.argv[1:])