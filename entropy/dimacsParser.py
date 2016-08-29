"""
	module for handling CNF files
"""
import random

def parser(cnfFile):
	""" in: cnf,
		out: cnf as list, num of variables """
	in_data = cnfFile
	cnf = list()
	cnf.append(list())
	maxvar = 0

	for line in in_data:
		tokens = line.split()
		if len(tokens) != 0 and tokens[0] not in ("p", "c"):
			for tok in tokens:
				lit = int(tok)
				maxvar = max(maxvar, abs(lit))
				if lit == 0:
					cnf.append(list())
				else:
					cnf[-1].append(lit)

	assert len(cnf[-1]) == 0
	cnf.pop()
	return cnf, maxvar

def generateDict(maxvar):
	""" in: num of variables
		out: dict of literals 1,-1,...n,-n """
	tupleList = list()
	for i in xrange(1,maxvar+1):
		tupleList.append((i,0))
		tupleList.append((-i,0))
	return dict([(x[0], x[1]) for x in tupleList])

def genRandomDict(maxvar,size):
	""" in: maxvar
		out: dict, a subset with Size=size of random literals """
	tupleList = list()
	allLits = [i for i in range(1,maxvar+1)]

	sample = random.sample(allLits,int(size*len(allLits)))
	for i in sample:
		tupleList.append((i,0))
		tupleList.append((-i,0))
	return dict([(x[0],x[1]) for x in tupleList])

def writeCnf(cnfList, numLits, numClauses):
	""" in: cnfList, numLits, clauses
		writes a cnf file dimacsDoc.txt """
	f = open("dimacsDoc.cnf", "w")
	s = "p cnf " + str(numLits) + " " + str(numClauses) + "\n"
	f.write(s)
	for clause in cnfList:
		s = ""
		for lit in clause:
			s += str(lit) + " "
		s+= str(0) + "\n"
		f.write(s)
	f.close()
