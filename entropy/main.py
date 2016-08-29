import dimacsParser
import runCounter
import histogram
import sys, getopt
import time
import os
from os import listdir
import csv
import shutil

def count(literalsDict, cnf, numVars, timeoutDur, totalSols):
	# validation check
	if numVars < 1:
		sys.exit("No variables in cnf")
	# iterate over all the positive (lit>0)
	for lit in (x for x in literalsDict.keys() if x>0):
		#print "analyzing literals {0} and {1}".format(lit,-lit)
		temp = list()
		temp.append(lit)
		# append lit as temp clause
		cnf.append(temp)
		# write cnf file
		dimacsParser.writeCnf(cnf, numVars, len(cnf))
		# solve
		if numVars <= 100:
			sols = runCounter.runCachet(timeoutDur)
		else:
			sols = runCounter.runSTS(timeoutDur,nsamples=1,k=5)
		literalsDict[lit] = sols
		literalsDict[-lit] = totalSols-sols
		cnf.pop()

def analyze(literalsDict, numVars):
	# update for every variable the relation (small/big solutions)
	tupleList = list()
	keys = literalsDict.keys()
	posKeys = [i for i in keys if i>0]
	for i in posKeys:
		small = min(literalsDict[i], literalsDict[-i])
		big = max(literalsDict[i], literalsDict[-i])
		tupleList.append((i, roundToEven(small,big)))
	return dict([(x[0], x[1]) for x in tupleList])

def roundToEven(small, big):
	# round to nearest even (float)
	num = (float(small) / big) * 10
	if num.is_integer():
		return num/10
	else:
		trunc = 2*round(num/2)
		return float(trunc)/10

def generateOutput(filename, literalsDict):
	head, tail = os.path.split(filename)
	outputFilename = tail.split('.cnf')[0] + '.txt'
	f = open(os.path.join(pathToOutput + '/output',outputFilename), "w")
	s = ""
	for key in sorted(literalsDict.keys(), reverse=True):
		s = ""
		s += str(key) + "," + str(literalsDict[key]) + "\n"
		f.write(s)
	f.close()

def generateEntropy(filename, entrop):
	head, tail = os.path.split(filename)
	outputFilename = tail.split('.cnf')[0] + '.txt'
	f = open(os.path.join(pathToOutput + '/entropy',outputFilename), "w")
	s = "Entropy:" + str(entrop)
	f.write(s)
	f.close()

def generateSols(filename,sols):
	head, tail = os.path.split(filename)
	outputFilename = tail.split('.cnf')[0] + '.txt'
	f = open(os.path.join(pathToOutput + '/sols',outputFilename), "w")
	s = "Solutions:" + str(sols)
	f.write(s)
	f.close

def singleFile(filename, pathToDir, timeoutDur):
	f = open(os.path.join(pathToDir,filename), "r")
	# compute cnf, num of vars, literals dictionary
	cnf, numVars = dimacsParser.parser(f)
	#literalsDict = dimacsParser.generateDict(numVars)
	literalsDict = dimacsParser.genRandomDict(numVars,0.6)
	dimacsParser.writeCnf(cnf, numVars, len(cnf))
	# compute number of solutions
	print "Calculating total num of sols"
	if numVars <= 100:
		numSols = runCounter.runCachet(timeoutDur)
	else:
		numSols = runCounter.runSTS(timeoutDur*20,nsamples=5,k=50)
	if numSols == 0:
		print "No solutions for this formula"
		return None, None
	# count backbone variables in dictionary
	count(literalsDict, cnf, numVars, timeoutDur, numSols)
	analyzeDict = analyze(literalsDict, numVars)
	histDict = histogram.sumFreqs(analyzeDict)
	# compute entropy
	entropy = histogram.calcEntropy(histDict, len(literalsDict)/2)
	# generate histogram
	histogram.generateHist(filename,pathToOutput + '/histogram', histDict, True)
	# generate output file
	generateOutput(filename, literalsDict)
	generateEntropy(filename, entropy)
	generateSols(filename, numSols)
	return entropy, numSols

def inCsv(formula):
	with open(resultsPath, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if len(row) != 0:
				if str(row[0]) == str(formula):
					return True
	return False

def allFiles(pathToDir, timeoutDur, csvFilesList, recursive, csvWriter, filterExisting):
	suffix = '.cnf'
	entropyDict = {}
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
		sys.exit("No CNF files in the path directory")

	print "Analyzing all cnf files in directory"
	print "--------------------------------"
	for f in allfiles:
		t3 = time.time()
		if filterExisting:
			if inCsv(f):
				print "Filtered " + str(f) 
				continue
		if len(os.path.split(f))>1:
			displayFile = os.path.split(f)[1]
		else:
			displayFile = os.path.split(f)
		print "Currently analyzing: " + str(displayFile) 
		entropy,numSols = singleFile(f, pathToDir, timeoutDur)
		# append entropies to csv after each file
		if numSols:
			csvWriter.writerow({'formula': f, 'entropy': entropy, 'num sols': numSols })
		#entropyDict[f] = entropy,numSols
		t4 = time.time()
		print "Analyzing took", t4-t3, "Seconds"
		print "--------------------------------"
	#sumEntropies(entropyDict, pathToOutput)

def appendEntropiesCsv(formula,entropy,numSols,directory):
	filename = os.path.join(pathToOutput,'entropies.csv')
	fileExists = os.path.isfile(filename)
	with open(filename, 'a') as f:
		fieldnames = ['formula', 'entropy', 'num sols']
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		if not fileExists:
			writer.writeheader()
		writer.writerow({'formula': formula, 'entropy': entropy, 'num sols': numSols })

def sumEntropies(entropyDict, directory):
	with open(os.path.join(pathToOutput,'entropies.csv'), 'w') as f:
		fieldnames = ['formula', 'entropy', 'num sols']
		#w = csv.DictWrite(f, entropyDict.keys(), fieldnames=fieldnames)
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for key in entropyDict:
			writer.writerow({'formula': key, 'entropy': entropyDict[key][0], 'num sols': entropyDict[key][1]})

def clearOutput(pathToOutput):
	output = pathToOutput + '/output'
	histogram = pathToOutput + '/histogram'
	entropy = pathToOutput + '/entropy'
	sols = pathToOutput + '/sols'
	for theFile in os.listdir(output):
		filePath = os.path.join(output, theFile)
		try:
			if os.path.isfile(filePath):
				os.unlink(filePath)
		except Exception, e:
			print e
	for theFile in os.listdir(histogram):
		filePath = os.path.join(histogram, theFile)
		try:
			if os.path.isfile(filePath):
				os.unlink(filePath)
		except Exception, e:
			print e
	for theFile in os.listdir(entropy):
		filePath = os.path.join(entropy, theFile)
		try:
			if os.path.isfile(filePath):
				os.unlink(filePath)
		except Exception, e:
			print e
	for theFile in os.listdir(sols):
		filePath = os.path.join(sols, theFile)
		try:
			if os.path.isfile(filePath):
				os.unlink(filePath)
		except Exception, e:
			print e

def extractFilenames(fname):
	filenames = []
	with open(fname, mode='r') as infile:
		reader = csv.reader(infile)
		for rows in reader:
			filenames.append(rows[0])

	return filenames

def main(argv):
	t1 = time.time()
	global cnf, numVars, literalsDict, numSols, analyzeDict, histDict, entropy, pathToOutput, resultsPath
	
	# path to directory of benchmarks
	pathToDir = ''
	# timeout duration for each running of counter
	timeoutDur = 100
	# optional csv file that contains a list of specified formulas
	csvFilesList = None
	# optional flag to recursively solve all formulas in the directory
	recursive = False
	# filter existing
	filterExisting = False

	# handle arguments
	try:
		opts, args = getopt.getopt(argv, "hrfp:t:l:")
	except getopt.GetoptError:
		print 'main.py -p <path> -t <timeout>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'main.py -p <path> -t <timeout>'
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
	pathToOutput = os.getcwd() + '/output'
	resultsfile = 'entropies.csv'
	resultsPath = os.path.join(pathToOutput, resultsfile)

	filename = os.path.join(pathToOutput,'entropies.csv')
	fileExists = os.path.isfile(filename)
	with open(filename, 'a',1) as csvfile:
		fieldnames = ['formula', 'entropy', 'num sols']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		if not fileExists:
			writer.writeheader()
		allFiles(pathToDir,timeoutDur,csvFilesList,recursive,writer,filterExisting)
		csvfile.flush()
	csvfile.close()

	# delete temp files
	filePath = os.getcwd() + '/dimacsDoc.cnf'
	try:
		if os.path.isfile(filePath):
				os.unlink(filePath)
	except Exception, e:
		print e

	#tests()

	t2 = time.time()
	print "Script running took ", t2-t1, " Seconds"

def tests():
	print "Number of solutions:" + str(numSols) + "\n"
	print "--------------------"
	print "Literals dictionary:\n"
	for key in literalsDict:
		print str(key) + ": " + str(literalsDict[key]) + "\n"
	print "--------------------"
	print "Analyze dictionary:\n"
	for key in analyzeDict:
		print str(key) + ": " + str(analyzeDict[key]) + "\n"
	print "--------------------"
	print "Histogram dictionary\n"
	for key in histDict:
		print str(key) + ": " + str(histDict[key]) + "\n"
	print "--------------------"
	print "Entropy\n"
	print entropy
	print "--------------------"
	if numVars <=150:
		print "Cachet"
	else:
		print "STS"

if __name__ == '__main__':
	main(sys.argv[1:])