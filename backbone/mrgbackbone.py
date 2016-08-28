import csv
import os, sys
import pandas as pd

def mergeBackbone():
    suffix = '.csv'
    
    exps = {
        1: 'exp1',
        2: 'exp2',
        3: 'exp3',
        4: 'exp4',
        5: 'exp5'
    }
    output = str(exps[int(exp)]) + '-results.csv'

    ## BACKBONES CSV FILE -> TO DICT
    # all files in dir (filter only csv) - assumes ONLY one csv file in dir
    backbones = os.listdir(path)
    backbones = [filename for filename in backbones if filename.endswith (suffix)]
    if not backbones:
        print "Input file of csv not found: " + str(path)
        sys.exit(2)

    # csv file
    backboneCsv = backbones[0]
    with open(os.path.join(path,backboneCsv)) as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        dict1 = {row[0]: row[1:] for row in r}

    ## EXP CSV FILE -> TO DICT
    allResults = os.listdir(expPath)
    allResults = [filename for filename in allResults if filename.endswith (suffix) and filename==output]

    if not allResults:
        print "Input file of experiement not found" + str(expPath)
        sys.exit(2)
    expCsv = allResults[0]

    with open(os.path.join(expPath,expCsv)) as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        dict2 = {row[0]: row[1:] for row in r}
    
    # intersection of keys
    keysA = set(dict1.keys())
    keysB = set(dict2.keys())

    keys = keysA & keysB

    bFile = os.path.join(os.path.join(path,backboneCsv))
    bFile = os.path.realpath(bFile)
    eFile = os.path.join(os.path.join(expPath, expCsv))
    eFile = os.path.realpath(eFile)

    outputDir = os.getcwd() + '/output/'
    outFile = os.path.join(outputDir,output)

    df1 = pd.read_csv(eFile)
    df = pd.read_csv(bFile)
    result = df1.merge(df, on="formula", how=str(join))
    result.to_csv(output, index=False)

    """
    merged = []
    for i in listOfTuples:
        for j in resultsList:
            if i[0] == 'formula' or j[0] == 'formula':
                continue
            fname = j[0].split('/')
            fname = fname[len(fname)-1]
            if fname == i[0]:
                j.append(i[1])
                result = (j[0], j[1:])
                merged.append(result)

    dict2 = dict(merged)

    with open(output, 'wb') as outfile:
        if int(exp) == 1:
            header = ["formula", "formulaType", "runtime","conflicts","runtime-NR","conflicts-NR", "entropy", "solutions", "backbone"]
        else:
            header = ["formula", "solver", "runtime","conflicts", "entropy", "solutions", "backbone"]
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        for key, value in dict2.items():
            writer.writerow([key,value])
    """
    if int(exp) == 1:
        header = ["formula", "formulaType", "runtime","conflicts","runtime-NR","conflicts-NR", "entropy", "solutions", "backbone"]
    else:
        header = ["formula", "formulaType", "solver", "runtime","conflicts", "entropy", "solutions", "backbone"]
    #pd.DataFrame(dict2).T.reset_index().to_csv(output,header=header,index=False)

def main(argv):
    global path, expPath, exp, join
    try:
        path = argv[0]
        expPath = argv[1]
        exp = argv[2]
        join = argv[3]
    except:
        print "mrgbackbone.py path expPath expNum joinType"
        sys.exit(2)

    mergeBackbone()

if __name__ == '__main__':
    main(sys.argv[1:])