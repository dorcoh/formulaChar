import subprocess, shlex
from threading import Timer
import sys, getopt
import time
import os
from os import listdir
import csv

def kill_proc(proc, timeout):
  	timeout["value"] = True
  	proc.kill()

def run(filename, executable, timeout_sec):
	""" run solver """
	runstring = './' + str(executable) + ' ' + str(filename)

	proc = subprocess.Popen(shlex.split(runstring), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  	timeout = {"value": False}
  	timer = Timer(timeout_sec, kill_proc, [proc, timeout])
  	timer.start()

	lines = list()
	for line in proc.stdout:
		lines.append(line)

	timer.cancel()
	if timeout["value"] == True:
		return 'TIMEOUT', 'TIMEOUT'
	# handle output
	#----------------------------------------
	matchingR = [s for s in lines if "CPU time" in s]
	matchingC = [s for s in lines if "c conflicts" in s]
	
	# check for valid output
	if not matchingR or not matchingC:
		if not matchingR:
			runtime = None
		if not matchingC:
			conflicts = None
	# valid
	else:
		conflicts =  matchingC[0].split()[3]	
		runtime = matchingR[0]
		runtime = runtime.split()[4]
	#----------------------------------------
	return float(runtime), int(conflicts)

def singleFile(filename, executable, timeout):
	return run(filename,executable, timeout)

def inCsv(formula, solver):
	with open(resultsPath, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if len(row) != 0:
				if str(row[0]) == str(formula) and str(row[1]) == str(solver):
					return True
	return False

def processingLoop(csvfile, solver, timeoutDur, pathToDir, csvFilesList, recursive, filterExisting, csv_writer):
	suffix = '.cnf'
	# extract all filenames from csv file
	if csvFilesList != None:
		filenames = []
		files = extractFilenames(csvFilesList)
		for f in files:
			path = os.path.join(os.getcwd(), pathToDir)
			path = os.path.join(path,f)
			path = os.path.realpath(path)
			filenames.append(path)
	# get all files from directory
	else:
		fullPath = os.path.join(os.getcwd(),pathToDir)
		fullPath = os.path.realpath(fullPath)
		# not recursive search
		if not recursive:
			files = listdir(fullPath)
			filenames = []
			for f in files:
				f = os.path.join(fullPath,f)
				filenames.append(f)
		# recursive search for files
		else:
			filenames = []
			for (dir, _ , files) in os.walk(fullPath):
				for f in files:
					path = os.path.join(dir,f)
					filenames.append(path)

	allfiles = [filename for filename in filenames if filename.endswith (suffix)]

	# raise an error if no files found
	if len(allfiles) == 0:
		sys.exit("No CSV files in the path directory")

	for f in allfiles:
		t1 = time.time()
		if filterExisting:
			if inCsv(f, solver):
				print "Filtered " + str(f) + " with solver " + str(solver) 
				continue
		# print file name currently solving
		if len(os.path.split(f))>1:
			displayFile = os.path.split(f)[1]
		else:
			displayFile = os.path.split(f)
		print "Currently solving: " + str(displayFile)
		
		runtime, conflicts = singleFile(f,solver,timeoutDur)
		if runtime != None:
			csv_writer.writerow({'formula': f, 'solver': solver, 'runtime': runtime, 'conflicts': conflicts})
			
		t2 = time.time()
		
		print "Running took: ", t2-t1, "Seconds"
		print "--------------------------------"

def main(argv):
	t1 = time.time()
	# path to directory of benchmarks
	pathToDir = ''
	# timeout duration for all formulas
	timeoutDur = 0
	# optional csv file that contains a list of specified formulas
	csvFilesList = None
	# optional flag to recursively solve all formulas in the directory
	recursive = False
	# optional flag to filter existing entries in csv
	filterExisting = False
	# solvers list
	solvers = ['wrapper-base.sh', 'wrapper-60.sh', 'wrapper-85.sh', 'wrapper-95.sh']
	solversDict = {'wrapper-base.sh': 'NR-0.5_G-0.95', 'wrapper-60.sh': 'NR-0.999_G-0.6', 'wrapper-85.sh': 'NR-0.999_G-0.85', 'wrapper-95.sh': 'NR-0.999_G-0.95'}

	# handle arguments
	try:
		opts, args = getopt.getopt(argv, "hrfp:t:l:")
	except getopt.GetoptError:
		print 'exp5.py -p <path> -t <timeout>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'exp5.py -p <path> -t <timeout>'
			print '-p <path> - The main path to the directory of the instances'
			print '-t <timeout> - Timeout duration to every formula solved'
			print 'Optional paramaeters:'
			print '-l <csvfilelist> - CSV file that contains formulas list in the path'
			print '-r (recursive)'
			print '-f (filter existing entries)'
			sys.exit()
		elif opt == '-r':
			recursive = True
		elif opt in ("-p"):
			pathToDir = arg
		elif opt in ("-t"):
			timeoutDur = int(arg)
		elif opt in ("-l"):
			csvFilesList = arg
		elif opt  == '-f':
			filterExisting = True

	# directory of the output
	global pathToOutput, resultsfile, resultsPath
	pathToOutput = os.getcwd() + '/output'
	resultsfile = 'results.csv'
	resultsPath = os.path.join(pathToOutput, resultsfile)

	# solve benchmarks for every solver
	
	file_exists = os.path.isfile(resultsPath)
	with open(os.path.join(pathToOutput, resultsfile), 'a', 1) as csvfile:
		fieldnames = ['formula', 'solver', 'runtime', 'conflicts']
		csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		# dont write header twice
		if not file_exists:
			csv_writer.writeheader()
		# solve benchmarks for every solver
		for solver in solvers:
			processingLoop(csvfile, solver, timeoutDur, pathToDir, csvFilesList, recursive, filterExisting, csv_writer)
			csvfile.flush()
		csvfile.close()

	t2 = time.time()
	print "Script running took ", t2-t1, " Seconds"
	#tests()

def tests():
	return None

if __name__ == '__main__':
	main(sys.argv[1:])