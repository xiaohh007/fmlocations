import numpy as np 
import math

def IsCircle(minpoint, maxpoint,minx,maxx, x, y, z):
    k = (maxpoint[1]-minpoint[1])/(maxpoint[0]-minpoint[0]) 
    zlist = []
    
    # print(len(x), len(y))
    for xi in x:
        yi = k*(xi - minpoint[0]) + minpoint[1]
        ycount = 0
        while ycount < len(y)-1:
            if abs(yi-y[ycount])<0.1:
                break
            else:
                ycount += 1
        if  not (math.isnan(z[ycount][x.index(xi)])) :
            zlist.append(z[ycount][x.index(xi)])     
    print(len(zlist), len(set(zlist)))
    if len(zlist) != len(set(zlist)):
        print(True)
    else:
        print(False)
    return [k, minpoint[0], minpoint[1], maxpoint[0]]
