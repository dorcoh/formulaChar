import csv

r = csv.reader(open('entropies.csv'))
lines = [l for l in r]
for l in lines:
	l[0] = l[0].replace('newInstances', 'CBS')

writer = csv.writer(open('output.csv', 'w'))
writer.writerows(lines)