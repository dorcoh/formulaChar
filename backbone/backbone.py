import sys,getopt
import csv
import os

def getNumVars(filename, pathToDir):
    # get num of variables from a file
    with open(os.path.join(pathToDir,filename), "r") as f:
        for i,l in enumerate(f):
            pass
        total = (i+1)/2
    return total

def singleFile(filename, pathToDir):
    # compute backbone for a singlefile

    # get num vars
    numVars = getNumVars(filename,pathToDir)

    solsList = []
    bb = 0
    # iterate over all sols in file
    with open(os.path.join(pathToDir,filename), "r") as f:
        for row in f:
            splitted = row.split(',')
            sols = int(splitted[1])
            if sols == 0:
                bb += 1

    # return backbone, numvars (e.g 0.9,100)
    return bb/float(numVars), numVars

def inCsv(formula):
    # check for existing files in csv
    with open(outFname, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if len(row) != 0:
                if str(row[0]) == str(formula):
                    return True
    return False

def procFilename(f):
    # process filename (.txt to .cnf) and add prefix
    # return full path
    formula = f.split('/')
    formula = formula[len(formula)-1]
    formula = formula.replace('.txt','.cnf')
    formula = str(prefix) + str(formula)
    return formula

def processLoop(pathToDir, csvWriter):
    # process all files in a directory
    suffix = '.txt'

    fullPath = os.path.join(os.getcwd(),pathToDir)
    fullPath = os.path.realpath(fullPath)
    
    files = os.listdir(fullPath)
    filenames = []
    for f in files:
        f = os.path.join(fullPath,f)

        filenames.append(f)
    
    allfiles = [filename for filename in filenames if filename.endswith (suffix)]
    # raise an error if no files found
    if len(allfiles) == 0:
        sys.exit("No TXT files in the path directory")

    print "Analyzing all txt (solutions) files in directory"
    print "--------------------------------"
    for f in allfiles:
        if filterExisting:
            if inCsv(f):
                print "Filtered " + str(f) 
                continue
        # extract filename to display
        if len(os.path.split(f))>1:
            displayFile = os.path.split(f)[1]
        else:
            displayFile = os.path.split(f)

        # analyze a single file
        print "Currently analyzing: " + str(displayFile) 
        backbone, numVars = singleFile(f, pathToDir)
        # append entropies to csv after each file
        csvWriter.writerow({'formula': procFilename(f), 'backbone': backbone})
        print "--------------------------------"

def main(argv):
    global pathToDir, fname, outputFile, resultsPath, filterExisting, outFname, prefix
    outputFile = 'backbone.csv'
    prefix = ''
    pathToDir = ''
    filterExisting = False

    try:
        opts, args = getopt.getopt(argv, "hfp:d:")
    except getopt.GetoptError:
        print 'backbone.py -p <path>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'backbone.py -p <path> -d <prefix>'
            print '-p <path> - The main path to the directory of the instances'
            print '-d <prefix> - prefix to add before formula name'
            print 'Optional paramaeters:'
            print '-f (filter existing entries)'
            sys.exit()
        elif opt in ("-p"):
            pathToDir = arg
        elif opt in ("-f"):
            filterExisting = True
        elif opt in ("-d"):
            prefix = arg

    resultsPath = os.getcwd()
    outFname = os.path.join(resultsPath,outputFile)
    fileExists = os.path.isfile(outFname)
    
    with open(outFname, 'a', 1) as csvfile:
        fieldnames = ['formula', 'backbone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not fileExists:
            writer.writeheader()
        processLoop(pathToDir,writer)
        csvfile.flush()
    csvfile.close()
    
    

if __name__ == '__main__':
    main(sys.argv[1:])