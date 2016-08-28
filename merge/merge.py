import csv
import os
import sys
import pandas as pd

"""
    merge two csv files based on the experience,
    assumes there are results in exp#/output/results.csv
    and releveant entropies (same formulas) in entropy/output/entropies.csv
"""
def merge(exp,formulaType):
    suffix = '.csv'
    exps = {
        1: 'exp1',
        2: 'exp2',
        3: 'exp3',
        4: 'exp4',
        5: 'exp5'
    }

    # get entropy path and exp path
    entropy = '../entropy/output'
    path = '../' + str(exps[int(exp)]) + '/output'

    # full exp path
    expPath = os.path.join(os.getcwd(), path)

    # results.csv
    # assumes ONLY ONE csv file in directory (any *.csv)
    allResults = os.listdir(expPath)
    allResults = [filename for filename in allResults if filename.endswith (suffix)]
    if not allResults:
        print "Input file of experiement not found: " + str(expPath)
        sys.exit(2)

    # entropies
    # assumes ONLY ONE csv file in directory (any *.csv)
    entropyPath = os.path.join(os.getcwd(), entropy)
    entropies = os.listdir(entropyPath)
    entropies = [filename for filename in entropies if filename.endswith (suffix)]
    if not entropies:
        print "Input file of entropies not found: " + str(entropyPath)
        sys.exit(2)
   
    # merge csv files
    f = entropies[0]
    # read all entropies from csv -> to dictionary
    with open(os.path.join(entropyPath,f)) as f:
        r = csv.reader(f, delimiter=',')
        dict2 = {row[0]: row[1:] for row in r}

    # read all results from csv -> to dictionary
    f = allResults[0]
    with open(os.path.join(expPath,f)) as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        dict1 = {row[0]: row[1:] for row in r}

    # intersection between those two dictionaries
    keysA = set(dict1.keys())
    keysB = set(dict2.keys())
    #keys = set(dict1.keys() + dict2.keys())
    keys = keysA & keysB

    # output settings
    filename = str(exps[exp]) + '-' + str(f)
    outputDir = os.getcwd() + '/output/'

    # write joint rows
    outFile = os.path.join(outputDir,filename)
    file_exists = os.path.isfile(outFile)

    rFile = os.path.join(os.path.join(expPath,allResults[0]))
    rFile = os.path.realpath(rFile)
    eFile = os.path.join(entropyPath,entropies[0])
    eFile = os.path.realpath(eFile)

    outFile = os.path.join(outputDir,filename)

    df1 = pd.read_csv(rFile)
    df = pd.read_csv(eFile)
    result = df1.merge(df, on="formula", how=str(join))
    result.insert(1,'formulaType',formulaType)
    result.to_csv(outFile, index=False)

"""
    if exp == 1:
        with open(outFile, 'w', 1) as f:
            w = csv.writer(f, delimiter=',')
            w.writerow(generateHeader(exp))
            # merge same keys only (no duplicate keys in exp 1)
            w.writerows([[key] + dict1.get(key, []) + dict2.get(key, []) for key in keys if key != 'formula'])
    else:
"""

def generateHeader(exp):
    exp = int(exp)
    if exp == 1:
        header = ["formula", "runtime","conflicts","runtime-NR","conflicts-NR", "entropy", "solutions"]
    else:
        header = ["formula", "solver", "runtime","conflicts", "entropy", "solutions"]
    return header


def main(argv):
    global join
    try:
        expNum = argv[0]
        formulaType = argv[1]
        join = argv[2]
    except:
        print "Enter experiment number (1-5) as an argument"
        sys.exit(2)
    merge(int(expNum),formulaType)

if __name__ == "__main__":
    main(sys.argv[1:])