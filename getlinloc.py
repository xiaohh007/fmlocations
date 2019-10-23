import connmysql
import bd09towgs84 as projtrans
import math

def getlineloc(minpoint, maxpoint):
    fmtdevices = connmysql.get_fmtdevice()
    fmtdloc = []
    for index, fmtdevice in fmtdevices.iterrows():
        wgsloc = projtrans.bd09_to_wgs84(float(fmtdevice['lon']), float(fmtdevice['lat']))       
        utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
        fmtdloc.append([utmloc[0]/1000, utmloc[1]/1000, fmtdevice['deviceid']])
    k = (maxpoint[1]-minpoint[1])/(maxpoint[0]-minpoint[0])
    C = minpoint[1] - k*minpoint[0]
    M = math.sqrt(k*k+1)
    do =500
    px, py =0, 0
    if maxpoint[0]>minpoint[0]:
        for fmt in fmtdloc:
            if fmt[0] > maxpoint[0]:
                dl = abs(k*fmt[0]-fmt[1]+C) / M
                dp = math.sqrt((fmt[1]-maxpoint[1])**2+(fmt[0]-maxpoint[0])**2)
                d = math.sqrt(dl*dl+dp*dp)
                if d < do:
                    do = d
                    px = fmt[0]
                    py = fmt[1]
    else:
        for fmt in fmtdloc:
            if fmt[0]<maxpoint[0]:
                dl = abs(k*fmt[0]-fmt[1]+C) / M
                dp = math.sqrt((fmt[1]-maxpoint[1])**2+(fmt[0]-maxpoint[0])**2)
                d = math.sqrt(dl*dl+dp*dp)
                if d < do:
                    do = d
                    px = fmt[0]
                    py = fmt[1]
    return px,py

def get1point(x, y):
    fmtdevices = connmysql.get_fmtdevice()
    fmtdloc = []
    do =500
    px, py =0, 0
    for index, fmtdevice in fmtdevices.iterrows():
        wgsloc = projtrans.bd09_to_wgs84(float(fmtdevice['lon']), float(fmtdevice['lat']))       
        utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
        fmtdloc.append([utmloc[0]/1000, utmloc[1]/1000, fmtdevice['deviceid']])

    for fmt in fmtdloc:
        dp = math.sqrt((fmt[0]-x)**2+(fmt[1]-y)**2)
        if dp>10  and dp<do:
            do = dp
            px = fmt[0]
            py = fmt[1]

    px = (2*x+px)/3
    py = (2*y+py)/3
    return px,py


def get2point(points, z):
    zminindex = z.index(min(z))
    zmaxindex = z.index(max(z))
    minpoint = points[zminindex]
    maxpoint = points[zmaxindex]
    fmtdevices = connmysql.get_fmtdevice()
    fmtdloc = []

    for index, fmtdevice in fmtdevices.iterrows():
        wgsloc = projtrans.bd09_to_wgs84(float(fmtdevice['lon']), float(fmtdevice['lat']))       
        utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
        fmtdloc.append([utmloc[0]/1000, utmloc[1]/1000, fmtdevice['deviceid']])
    k = (maxpoint[1]-minpoint[1])/(maxpoint[0]-minpoint[0])
    C = minpoint[1] - k*minpoint[0]
    M = math.sqrt(k*k+1)
    if (max(z)-min(z))<2:        
        x0 = (minpoint[0] + maxpoint[0])/2
        y0 = (minpoint[1] + maxpoint[1])/2
    else:
        x0 = (minpoint[0] + 2*maxpoint[0])/3
        y0 = (minpoint[1] + 2*maxpoint[1])/3
        
    k1 = -1/k
    C1 = y0 - k1*x0
    M1 = math.sqrt(k1*k1+1)
    do =500
    px, py =0, 0

    for fmt in fmtdloc:
        dl = abs(k*fmt[0]-fmt[1]+C) / M
        dl1 = abs(k1*fmt[0]-fmt[1]+C1) / M1
        d = math.sqrt(dl*dl+dl1*dl1)
        if d < do:
            do = d
            px = fmt[0]
            py = fmt[1]

    # print(px,py)
    px = (px+maxpoint[0])/2
    py = (py+maxpoint[1])/2          
    return px,py