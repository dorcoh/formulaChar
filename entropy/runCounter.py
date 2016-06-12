"""
module to run the model counter
CNF assumed to be built (dimacsDoc.txt)
"""
import subprocess
import sys
from threading import Timer

def kill_proc(proc, timeout):
  	timeout["value"] = True
  	proc.kill()

def runCachet(timeout_sec):
	""" run Cachet model counter and return num of solutions """
	process = subprocess.Popen("./cachet dimacsDoc.cnf -q", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	timeout = {"value": False}
  	timer = Timer(timeout_sec, kill_proc, [process, timeout])
  	timer.start()

	lines = list()
	for line in process.stdout:
		lines.append(line)

	timer.cancel()
	if timeout["value"] == True:
		return 0
	# handle cachet output
	#----------------------------------------
	matching = [s for s in lines if "Number of solutions" in s]
	solString = matching[0]
	solString = solString.split()
	#----------------------------------------
	process.wait()
	# return number of solutions
	if not matching:
		return 0
	return int(float(solString[3]))

def runSTS(timeout_sec):
	""" run sample tree model counter, return num of solutions """
	lines = list()

	process = subprocess.Popen("./STS dimacsDoc.cnf", shell=True, stdout=subprocess.PIPE)
	
	timeout = {"value": False}
  	timer = Timer(timeout_sec, kill_proc, [process, timeout])
  	timer.start()

	for line in process.stdout:
		lines.append(line)
	
	timer.cancel()
	if timeout["value"] == True:
		return 0

	matching = [s for s in lines if "Different" in s]
	process.wait()
	if not matching:
		return 0
	return int(float(matching[0].split()[2]))

def runAMC(timeout_sec):
	""" run sample tree model counter, return num of solutions """
	process = subprocess.Popen("python ApproxMC.py -delta=0.2 -epsilon=0.9 dimacsDoc.cnf", shell=True, stdout=subprocess.PIPE)
	
	timeout = {"value": False}
  	timer = Timer(timeout_sec, kill_proc, [process, timeout])
  	timer.start()

	lines = list()
	for line in process.stdout:
		lines.append(line)
	
	timer.cancel()
	if timeout["value"] == True:
		return 0

	matching = [s for s in lines if "is" in s]
	solString = matching[0].split()
	if not matching:
		return 0
	return int(float(solString[len(solString)-1]))