import subprocess

def runGenerator(n,m,filename,c=80,k=3):
	runstring = "./generator -n {0} -m {1} -c {2} -k {3} > {4}".format(n,m,c,k,filename)
	print runstring
	process = subprocess.Popen(runstring, shell=True, stdout=subprocess.PIPE)
	for line in process.stdout:
		print line
	process.wait()

def main():
	variables = [240,400,800,1200,2000]
	for n in variables:
		m = int(4.13*n)
		for i in range(0,1000):
			filename = "vars-{0}-clauses-{1}-id-{2}.cnf".format(n,m,i)
			runGenerator(n,m,filename)

if __name__ == '__main__':
	main()