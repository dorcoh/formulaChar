import csv
from os import listdir
import os

def sumFreqs(analyzeDict):
	""" sum all the frequencies into a dictionary
		input: analyzed dictionary (all relations) """
	ranges = [x/10.0 for x in range(0,11)]
	histDict = dict([(p,0) for p in ranges])
	for key in analyzeDict:
		histDict[analyzeDict[key]] += 1
	return histDict

def calcEntropy(histDict, numVars):
	entropy = 0
	for k in histDict:
		perecent = float(histDict[k]) / numVars
		entropy += perecent * k
	return entropy

def generateHist(filename, directory, histDict, splitFileName = False):
	""" input: filename
		writes histogram as a csv file,
		name of the file will be input filename """
	head, tail = os.path.split(filename)
	# split filename if needed (formula.cnf -> formula.csv)
	if splitFileName == True:
		outputfilename = tail.split('.cnf')[0] + '.csv'
	with open(os.path.join(directory,outputfilename), 'w') as csvfile:
		fieldnames = ['relation', 'sum']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for key in histDict:
			writer.writerow({'relation': key, 'sum': histDict[key]})

def findCsvFilenames(pathToDir, suffix=".csv"):
	""" input: path to dir, suffix=csv (default)
		returns a list of file names """
	filenames = listdir(pathToDir)
	return [ filename for filename in filenames if filename.endswith ( suffix )]

def sumHistograms(pathToDir=os.getcwd()):
	""" input: path to directory
		generates the sum of all histograms (csv files) in the directory 
		writes a new file sum.csv as the new summarized histogram """
	# get all filenames
	filenames = findCsvFilenames(pathToDir)
	if len(filenames) == 0:
		sys.exit("No CSV files in the directory")
	# construct ranges dictionary as helper
	ranges = [x/10.0 for x in range(0,11)]
	histDict = dict([(p,0) for p in ranges])
	# sum all relations from files to the helper dictionary
	for f in filenames:
		with open(f, 'rb') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				histDict[float(row['relation'])] += int(row['sum'])
	generateHist('sum.csv', histDict)
