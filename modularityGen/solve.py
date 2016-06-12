import subprocess
import sys
from os import listdir
import os
from threading import Timer

def kill_proc(proc, timeout):
  	timeout["value"] = True
  	proc.kill()

def runSolver(filename, timeout_sec):
	runstring = "minisat {0}".format(filename)
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
	solString = matching[0]
	solString = solString.split()[0]

	process.wait()

	if solString == "UNSATISFIABLE":
		return 0
	elif solString == "SATISFIABLE":
		return 1

def main():
	suffix = '.cnf'
	filenames = listdir(os.getcwd())
	allFiles = [filename for filename in filenames if filename.endswith (suffix)]
	# raise an error if no files found
	if len(allFiles) == 0:
		sys.exit("No CNF files in the path directory")

	for f in allFiles:
		print "Currently solving " + str(f)
		status = runSolver(f, 100)
		if status == 0:
			filePath = os.path.join(os.getcwd(),f)
			print filePath
			try:
				if os.path.isfile(filePath):
					os.unlink(filePath)
				print "Deleted file " + str(f)
			except Exception, e:
				print e
	

if __name__ == '__main__':
	main()