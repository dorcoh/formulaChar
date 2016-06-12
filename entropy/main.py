import dimacsParser
import runCounter
import histogram
import sys, getopt
import time
import os
from os import listdir
import csv
import shutil

def count(literalsDict, cnf, numVars, timeoutDur):
	for key in literalsDict:
		temp = list()
		temp.append(key)
		# append literal as a temp clause
		cnf.append(temp)
		# write cnf file again
		dimacsParser.writeCnf(cnf, numVars, len(cnf))
		# get and update num of solutions
		# NEED TO EDIT
		if numVars <= 100:
			solutions = runCounter.runCachet(timeoutDur)
		else:
			solutions = runCounter.runSTS(timeoutDur)
		literalsDict[key] = solutions
		# remove temp clause
		cnf.pop()

def analyze(literalsDict, numVars):
	# update for every variable the relation (small/big solutions)
	tupleList = list()
	for i in xrange(1, numVars+1):
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
	outputFilename = filename.split('.cnf')[0] + '.txt'
	f = open(os.path.join(pathToOutput + '/output',outputFilename), "w")
	s = ""
	for key in sorted(literalsDict.keys(), reverse=True):
		s = ""
		s += str(key) + "," + str(literalsDict[key]) + "\n"
		f.write(s)
	f.close()

def generateEntropy(filename, entrop):
	outputFilename = filename.split('.cnf')[0] + '.txt'
	f = open(os.path.join(pathToOutput + '/entropy',outputFilename), "w")
	s = "Entropy:" + str(entrop)
	f.write(s)
	f.close()

def singleFile(filename, pathToDir, timeoutDur):
	f = open(os.path.join(pathToDir,filename), "r")
	# compute cnf, num of vars, literals dictionary
	cnf, numVars = dimacsParser.parser(f)
	literalsDict = dimacsParser.generateDict(numVars)
	dimacsParser.writeCnf(cnf, numVars, len(cnf))
	# compute number of solutions
	if numVars <= 100:
		numSols = runCounter.runCachet(timeoutDur)
	else:
		numSols = runCounter.runSTS(timeoutDur)
	if numSols == 0:
		print "No sultions for this formula"
		return None, None
	# count backbone variables in dictionary
	count(literalsDict, cnf, numVars, timeoutDur)
	analyzeDict = analyze(literalsDict, numVars)
	histDict = histogram.sumFreqs(analyzeDict)
	# compute entropy
	entropy = histogram.calcEntropy(histDict, numVars)
	# generate histogram
	histogram.generateHist(filename,pathToOutput + '/histogram', histDict, True)
	# generate output file
	generateOutput(filename, literalsDict)
	generateEntropy(filename, entropy)
	return entropy, numSols

def allFiles(pathToDir, timeoutDur, csvFilesList, recursive):
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
		if len(os.path.split(f))>1:
			displayFile = os.path.split(f)[1]
		else:
			displayFile = os.path.split(f)
		print "Currently analyzing: " + str(displayFile) 
		entropy,numSols = singleFile(f, pathToDir, timeoutDur)
		entropyDict[f] = entropy,numSols
		t4 = time.time()
		print "Analyzing took", t4-t3, "Seconds"
		print "--------------------------------"
	sumEntropies(entropyDict, pathToOutput)

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

def extractFilenames(fname):
	filenames = []
	with open(fname, mode='r') as infile:
		reader = csv.reader(infile)
		for rows in reader:
			filenames.append(rows[0])

	return filenames

def main(argv):
	t1 = time.time()
	global cnf, numVars, literalsDict, numSols, analyzeDict, histDict, entropy, pathToOutput
	
	# path to directory of benchmarks
	pathToDir = ''
	# timeout duration for each running of counter
	timeoutDur = 100
	# optional csv file that contains a list of specified formulas
	csvFilesList = None
	# optional flag to recursively solve all formulas in the directory
	recursive = False

	# handle arguments
	try:
		opts, args = getopt.getopt(argv, "hrp:t:l:")
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
			sys.exit()
		elif opt == '-r':
			recursive = True
		elif opt in ("-p"):
			pathToDir = arg
		elif opt in ("-t"):
			timeoutDur = int(arg)
		elif opt in ("-l"):
			csvFilesList = arg

	# directory of the output
	pathToOutput = os.getcwd() + '/output'

	allFiles(pathToDir,timeoutDur,csvFilesList,recursive)

	# delete temp files
	filePath = os.getcwd() + '/dimacsDoc.cnf'
	try:
		if os.path.isfile(filePath):
				os.unlink(filePath)
	except Exception, e:
		print e

	t2 = time.time()
	print "Script running took ", t2-t1, " Seconds"
	#tests()


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
	if numVars <=100:
		print "Cachet"
	else:
		print "AC"

if __name__ == '__main__':
	main(sys.argv[1:])