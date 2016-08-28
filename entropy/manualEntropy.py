import os
import csv

def genEntropy(path):
	files = os.listdir(path)
	addpath = '/home/sdorco/gen400/'
	txt = [f for f in files if f.endswith('.txt')]
	tupleList = []
	for f in files:
		fname = f.split('.txt')[0] + str('.cnf')
		k = addpath + str(fname)
		with open(os.path.join(path,f),'r') as txtfile:
			entropy = txtfile.read().split('Entropy:')
			e = entropy[1]
			tupleList.append((k,e))
	return dict(tupleList)

def sumEntropies(entropyDict, directory):
	with open(os.path.join(pathToOutput,'entropiesForced.csv'), 'w') as f:
		fieldnames = ['formula', 'entropy']
		#w = csv.DictWrite(f, entropyDict.keys(), fieldnames=fieldnames)
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for key in entropyDict:
			writer.writerow({'formula': key, 'entropy': entropyDict[key]})

def main():
	global pathToOutput
	# directory of the output
	pathToOutput = os.getcwd() + '/output'
	inputPath = os.getcwd() + '/output/entropy'

	#print inputPath
	entDict = genEntropy(inputPath)
	sumEntropies(entDict, pathToOutput)
	#sumEntropies()


if __name__ == '__main__':
	main()