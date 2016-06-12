import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
import csv
import sys
import os

"""
    input:
        csv filename,
        column number,
        list of formulas
    output:
        column filtered
"""
def getColumn(filename, column, filter=None):
    results = csv.reader(open(filename))
    results.next()
    # no filter
    if filter == None:
        return [result[column] for result in results]
    # filter
    else:
        return [result[column] for result in results if result[0] in filter]

"""
    input: exp number
    output: full path
"""
def getExpFilename(exp):
    exps = {
        1: 'exp1',
        2: 'exp2',
        3: 'exp3',
        4: 'exp4',
        5: 'exp5'
    }
    path = '../merge/output'
    filename = str(exps[int(exp)]) + '-results.csv'
    return os.path.join(path, filename)

"""
    generates all graphs of exp1
"""
def plotExp1():
    filename = getExpFilename(1)
    # get all entrpoies
    formulas = getColumn(filename, 0)
    entropies = getColumn(filename, 5)
    entDict = dict(zip(formulas, entropies))
    clusterDict = {
        '(0,0.1]': list(),
        '(0.1,0.2]': list(),
        '(0.2,0.3]': list(),
        '(0.3,0.4]': list(),
        '(0.4,1]': list()
    }
    # cluster to groups
    for f in entDict:
        entropy = float(entDict[f])
        if 0 < entropy <= 0.1:
            clusterDict['(0,0.1]'].append(f)
        elif 0.1 < entropy <= 0.2:
            clusterDict['(0.1,0.2]'].append(f)
        elif 0.2 < entropy <= 0.3:
            clusterDict['(0.2,0.3]'].append(f)
        elif 0.3 < entropy <= 0.4:
            clusterDict['(0.3,0.4]'].append(f)
        elif 0.4 < entropy <= 1:
            clusterDict['(0.4,1]'].append(f)

    # plot - runtimes
    f, axarr = plt.subplots(2, 3, figsize=(20,20))
    i,j = 0,0
    for c in sorted(clusterDict):
        x = getColumn(filename,1,clusterDict[c])
        y = getColumn(filename,3,clusterDict[c])
        label = "Entropies: " + str(c)
        axarr[i,j].scatter(x,y)
        axarr[i,j].set_title(label)

        if j < 2:
            j += 1
        else:
            i += 1
            j = 0

    plt.savefig('exp1-runtimes-byEntropy.png')

    # plot - differences
    f, axarr = plt.subplots(2, 3, figsize=(20, 20))
    i, j = 0, 0
    for c in sorted(clusterDict):
        x = getColumn(filename, 2, clusterDict[c])
        y = getColumn(filename, 4, clusterDict[c])
        z = list()
        for k in xrange(0, len(x) - 1):
            diff = int(x[k]) - int(y[k])
            diff = (float(diff) / int(y[k]))
            diff *= 100
            z.append(diff)
        label = "Entropies: " + str(c)
        if not z:
            axarr[i, j].set_title(label+str(' No values'))
        else:
            axarr[i, j].stem(z, linefmt='b-', markerfmt='bo', basefmt='r-')
            axarr[i, j].set_title(label)

        if j < 2:
            j += 1
        else:
            i += 1
            j = 0

    plt.savefig('exp1-conflicts-byEntropy.png')

def main(argv):
    try:
        expNum = argv[0]
    except:
        print "Enter experiment number (1-5) as an argument"
        sys.exit(2)

    filename = getExpFilename(expNum)

    #scatterPlot(filename, 1, 3, 'myfig')
    #plotExp(expNum)
    plotExp1()


if __name__ == "__main__":
    main(sys.argv[1:])