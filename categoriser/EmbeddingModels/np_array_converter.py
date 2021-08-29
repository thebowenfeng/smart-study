import numpy as np
FILE_NAME = "glove50weights.txt"
LINES = 400000
k = open(FILE_NAME, "r").read().split('\n')
res=[]

for i in range(LINES):
    if i%10000 == 0:
        print(i)
    if len(k[i]) <= 5:
        break
    else:
        res.append(np.fromstring(k[i], sep=" "))

np.array(res).tofile('glove50BinWeights.dat')
