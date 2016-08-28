import csv
import sys
import os

def addPrefix():
    fullPath = os.path.join(os.getcwd(),fname)
    tupList = []
    with open(fullPath, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[0] == 'formula':
                header = row
                continue
            formula = row[0].split('/')
            formula = formula[len(formula)-1]
            formula = formula.replace('.txt','.cnf')
            formula = str(prefix) + str(formula)
            row[0] = formula
            print row
            #row[0] = formula

def main(argv):
    global fname, prefix
    try:
        fname = argv[0]
        prefix = argv[1]
    except:
        print "mini.py filename prefix"
        sys.exit(2)
    addPrefix()

if __name__ == '__main__':
    main(sys.argv[1:])