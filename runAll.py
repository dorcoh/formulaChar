import subprocess, shlex
from threading import Timer
import time
import os

def runScript(script, path):
	runstring = 'python -u ' + str(script)
	process = subprocess.Popen(runstring, shell=True, cwd=path)
	process.wait()

def main():
	t1 = time.time()
	exp1 = os.getcwd() + '/exp1'
	path1 = exp1 + '/exp1.py'
	exp2 = os.getcwd() + '/exp2'
	path2 = exp2 + '/exp2.py'
	exp3 = os.getcwd() + '/exp3'
	path3 = exp3 + '/exp3.py'
	exp4 = os.getcwd() + '/exp4'
	path4 = exp4 + '/exp4.py'
	exp5 = os.getcwd() + '/exp5'
	path5 = exp5 + '/exp5.py'

	pathDict = {exp1: path1, exp2: path2, exp3: path3, exp4: path4, exp5: path5}

	for e in pathDict:
		print 'Currently running: ' + str(e)
		runScript(pathDict[e],e)

	t2 = time.time()
	print "Script running took ", t2-t1, " Seconds"

def tests():
	return None

if __name__ == '__main__':
	main()