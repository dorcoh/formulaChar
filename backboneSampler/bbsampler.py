import subprocess,shlex
from threading import Timer
import os,sys,getopt
import csv
import time

def kill_proc(proc, timeout):
  	timeout["value"] = True
  	proc.kill()

def run(fName,executable,path,timeoutSec):
	runstring = "./{0} {1}".format(executable,
		                           fName)

	proc = subprocess.Popen(shlex.split(runstring),
		                    stdout=subprocess.PIPE,
		                    stderr=subprocess.PIPE)

	timeout = {"value": False}
	timer = Timer(timeoutSec,kill_proc,[proc,timeout])
	timer.start()

	samples = list()

	# parse output and save into dict
	sampId = 1
	conflicts,cpuTime = None,None
	sat = None
	for line in proc.stdout:
		if line:
			if 'conflicts' in line:
				conflicts = line.split(':')[1].split()[0]
			if 'CPU' in line:
				cpuTime =  line.split(':')[1].split()[0]
			if 'SATISFIABLE' in line:
				if line.split()[0] == 'SATISFIABLE':
					sat = True
				elif line.split()[0] == 'UNSATISFIABLE':
					sat = False
			if line[0] != '#':
				continue
			# total decisions
			if line[0] == '#' and line[1] == '#':
				out = line[2:].split(',')
				totalDec = int(out[0].split(':')[1])
			out = line[1:].split(',')
			decisions = int(out[0].split(':')[1])
			backbone = float(out[1].split(':')[1])
			sampTup = (fName,sampId,decisions,backbone,
				       conflicts,cpuTime)
			samples.append(sampTup)
			sampId += 1

	timer.cancel()
	if timeout["value"] == True:
		return 'TIMEOUT'

	return samples,totalDec,sat

def extractFilenames(fname):
	filenames = []
	with open(fname, mode='r') as infile:
		reader = csv.reader(infile)
		for rows in reader:
			filenames.append(rows[0])

	return filenames

def inCsv(formula):
	with open(resultPath, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if len(row) != 0:
				if str(row[0]) == str(formula):
					return True
	return False

def processLoop(pathToDir,timeout,csvFilesList,csvWriter,filterExisting):
	suffix = '.cnf'
	
	# extract filenames from csv file
	if csvFilesList:
		fileNames = []
		files = extractFilenames(csvFilesList)
		for f in files:
			path = os.path.join(os.getcwd(), pathToDir)
			path = os.path.join(path,f)
			path = os.path.realpath(path)
			fileNames.append(path)
	# extract filenames from listdir
	else:
		path = os.path.join(os.getcwd(),pathToDir)
		path = os.path.realpath(path)
		files = os.listdir(path)
		fileNames = []
		for f in files:
			f = os.path.join(path,f)
			fileNames.append(f)

	allFiles = [fname for fname in fileNames if \
				fname.endswith(suffix)]
	if len(allFiles) == 0:
		sys.exit("No CNF files in the directory")

	# loop through all files
	for f in allFiles:
		if filterExisting:
			if inCsv(f):
				print "Filtered" + str(f)
				continue
		t1 = time.time()
		if len(os.path.split(f))>1:
			displayFile = os.path.split(f)[1]
		else:
			displayFile = os.path.split(f)
		print "Currently solving: " + str(displayFile)

		ret = run(f,'minisat',pathToDir,timeout)
		t = 'TIMEOUT'
		if ret != t:
			# no timeout
			samples,totalDec,sat = ret	
			for row in samples:
				csvWriter.writerow({
						'formula': f,
						'sampId': row[1],
						'decisions': row[2],
						'decisionsNormalized': float(row[2])/totalDec, 
						'backbone': row[3],
						'conflicts': row[4],
						'cpu': row[5],
						'sat': sat
					})
		else:
			# timeout, fill fields with 'TIMEOUT'
			csvWriter.writerow({
					'formula': f,
					'sampId': t,
					'decisions': t,
					'decisionsNormalized': t, 
					'backbone': t,
					'conflicts': t,
					'cpu': t,
					'sat': t
				})		
		t2 = time.time()
		print "Running took: ", t2-t1, "Seconds"
		print "--------------------------------"

def main(argv):
	pathToDir = ''
	timeout = 0
	csvFilesList = None
	filterExisting = False

	try:
		opts, args = getopt.getopt(argv,"hfp:t:l:")
	except:
		print 'bbsampler.py -p <path> -t <timeout>'
		sys.exit(2)

	for opt,arg in opts:
		if opt == '-h':
			print 'bbsampler.py -p <path> -t <timeout>'
			print 'Optional paramaeters:'
			print '-l <csvfilelist> - CSV file that contains formulas list in the path'
			print '-f - filter existing files on csv'
			sys.exit(2)
		elif opt == '-p':
			pathToDir = arg
		elif opt == '-t':
			timeout = int(arg)
		elif opt == '-l':
			csvFilesList = arg
		elif opt == '-f':
			filterExisting = True

	pathOutput = os.getcwd() + '/output'
	resultsFile = 'results.csv'

	global resultPath
	resultPath = os.path.join(pathOutput, resultsFile)

	fileExists = os.path.isfile(resultPath)
	with open(resultPath,'a',1) as csvfile:
		header = ['formula','sampId','decisions',
			  	  'decisionsNormalized','backbone', 'cpu',
			  	  'conflicts','sat']
		csvWriter = csv.DictWriter(csvfile,
								   fieldnames=header)
		if not fileExists:
			csvWriter.writeheader()
		processLoop(pathToDir,timeout,csvFilesList,
					csvWriter,filterExisting)
		csvfile.flush()

	csvfile.close()

if __name__ == '__main__':
	main(sys.argv[1:])