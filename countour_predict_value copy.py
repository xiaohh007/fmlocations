# -*- coding:utf-8 -*-
import rssiclean
import numpy as np 
import pandas as pd 
from pandas import Series
import connmysql
import math
from scipy.optimize import curve_fit
import bd09towgs84 as projtrans
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d  import Axes3D
import scipy.signal as signal
import countor_predvex

def pred_location(fm, starttime, endtime):
    result = connmysql.get_fmdata(fm, starttime , endtime)
    data_clean = rssiclean.get_rssidata_c(result)
    xy_vex = countor_predvex.get_predvex(starttime , endtime)
    x = []
    y = []
    z = []
    utmloc_0 =[]
    locpx = 0
    locpy = 0
    for data in data_clean:
        wgsloc = projtrans.bd09_to_wgs84(float(data['lon']), float(data['lat']))
        wgsloc_0 = projtrans.bd09_to_wgs84(float(data['fmlon']), float(data['fmlat']))
        utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
        utmloc_0 = projtrans.wgs2utm(wgsloc_0[0], wgsloc_0[1])
        data['lon'],data['lat'] = utmloc[0], utmloc[1]
        data['fmlon'],data['fmlat'] = utmloc_0[0], utmloc_0[1]
        x.append(utmloc[0]/1000)
        y.append(utmloc[1]/1000)
        z.append(data['db'])
    print(utmloc_0)
    print(z)
    print(x)
    print(y)


    if len(z)<8 and max(z)>-45 and max(z)<-40:
        print(max(z))
        zindex = z.index(max(z))
        locpx, locpy = x[zindex], y[zindex]
        print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
    elif len(z)<7:
        print(max(z))
        zindex = z.index(max(z))
        print(x[zindex], y[zindex])
        print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
    else:
        points=[]
        px = []
        py = []
        for i in range(len(x)):
            point=[]
            point.append(x[i])
            px.append(x[i])
            point.append(y[i])
            py.append(y[i])   
            points.append(point)
        points=np.array(points)

        print(utmloc_0)
        print("X的差值：",max(x)-min(x))
        print("Y的差值：",max(y)-min(y))
        print("Z的max：",max(z))

        xinternal = 0.1
        yinternal = 0.1

        xstep = int((max(x)-min(x))/xinternal)
        ystep = int((max(y)-min(y))/yinternal)
        xxi=np.linspace(min(x),max(x),xstep)
        yyi=np.linspace(min(y),max(y),ystep)


        xi,yi=np.meshgrid(xxi,yyi)
        # print("xymeshgrid",xi, yi)
        zi=griddata(points,z,(xi,yi),method='cubic')#, fill_value=-10
        # print(xi.shape,yi.shape, zi.shape[0],zi.shape[1])

        locpreds = []
        zpred = []
        pi=0
        while pi < len(px):
            
            locx = int((px[pi] - min(x)) //xinternal)
            locy = int((py[pi]- min(y)) //yinternal)

            # print(locx,locy)
            temp = 0
            while locx < len(xxi)-1 and locy<len(yyi)-1:
                if zi[locy][locx]<zi[locy+1][locx]:
                    locy += 1
                elif zi[locy][locx]<zi[locy][locx+1]:
                    locx += 1
                elif zi[locy][locx]<zi[locy-1][locx]:
                    locy -= 1
                elif zi[locy][locx]<zi[locy][locx-1]:
                    locx -= 1 
                else:
                    # print(locx, locy)
                    print(zi[locy][locx])
                    if abs(zi[locy][locx] - max(z))<5 or zi[locy][locx] > max(z):
                        locpreds.append([min(x)+locx*xinternal, min(y)+locy*yinternal])
                    break       
            pi += 1

        locpred = np.array(list(set([tuple(t) for t in locpreds])))
        locpx =0
        locpy =0
        count = 0
        # for locp in locpreds:
        #     vexp = math.sqrt((locp[1]*1000-utmloc_0[1])**2+(locp[0]*1000-utmloc_0[0])**2)
        #     print(locp, vexp)

        # print("------------------")
        resdata = []

        for locp in locpred:
            count = 0
            for locps in locpreds:
                # print((np.array(locp)==np.array(locps)).all())
                if (np.array(locp)==np.array(locps)).all():
                    count += 1
            print(locp, count)
            locpx += locp[0]*count
            locpy += locp[1]*count
        if len(locpreds)>0:
            locpx = locpx / len(locpreds)
            locpy = locpy / len(locpreds)
            # print(locpx, locpy)
            # print(math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))

        print(locpx, locpy)
        
        print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))

        print(xy_vex)
        locpx -= xy_vex[0]
        locpy -= xy_vex[1]
        print(locpx, locpy)
        
        print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))

    # locpx=0
    # locpy=0
    # count=0
    # for locp in locpred:
    #     vexp = math.sqrt((locp[1]*1000-utmloc_0[1])**2+(locp[0]*1000-utmloc_0[0])**2)
    #     print(locp, vexp)
    #     locpx += locp[0]
    #     locpy += locp[1]
    #     count += 1
    # if count>0:
    #     locpx = locpx /count
    #     locpy = locpy /count
    #     print(locpx, locpy)
    #     print(math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
    #     print("真实值",utmloc_0)






        # plt.contourf(xi,yi,zi,8,alpha=1,cmap=plt.cm.hsv)#画上颜色
        # c = plt.contour(xi,yi,zi,[0,10]) #等高线绘制
        # plt.plot(px,py,'ro')

        # plt.plot(utmloc_0[0]/1000,utmloc_0[1]/1000,'yo')
        # # 线条标注的绘制
        # plt.clabel(c,inline=True,fontsize=10)
        # # plt.show()

        # fig = plt.figure()
        # ax = plt.axes(projection='3d')
        # ax.contour3D(xi, yi, zi, 50, cmap='CMRmap')
        # ax.set_xlabel('x')
        # ax.set_ylabel('y')
        # ax.set_zlabel('z')
        # #调整观察角度和方位角。这里将俯仰角设为60度，把方位角调整为35度
        # ax.view_init(60, 35)
        # plt.show()










    # zz = zi.flatten()
    # print(zz.shape)
    # print(zz[signal.argrelextrema(zz, np.greater)])
    # zzloc = signal.argrelextrema(zz, np.greater)
    # zzvalue = zz[signal.argrelextrema(zz, np.greater)].tolist()
    # # print(zzloc)
    # print(max(zzvalue))
    # print(zzvalue.index(max(zzvalue)))
    # print(zzloc[0][zzvalue.index(max(zzvalue))])
    # shang = zzloc[0][zzvalue.index(max(zzvalue))] // zi.shape[1] / yinternal * (max(y)-min(y)) + min(y)
    # yu = zzloc[0][zzvalue.index(max(zzvalue))] % zi.shape[1] / xinternal * (max(x)-min(x)) + min(x)

    # vex = math.sqrt((shang*1000-utmloc_0[1])**2+(yu*1000-utmloc_0[0])**2)

    # print(shang, yu, min(x), min(y) , xinternal, yinternal)
    # print(vex)

    # lockmean = []
    # for zvalue in zzloc[0]:
    #     shang = zvalue // zi.shape[1] / yinternal * (max(y)-min(y)) + min(y)
    #     yu = zvalue % zi.shape[1] / xinternal * (max(x)-min(x)) + min(x)

    #     vex = math.sqrt((shang*1000-utmloc_0[1])**2+(yu*1000-utmloc_0[0])**2)
    #     lockmean.append([yu, shang])
    #     print(shang, yu, vex)

    # from sklearn.cluster import KMeans
    # lockmeanarray = np.array(lockmean)
    # k=25
    # clf = KMeans(n_clusters=k)
    # y_pred = clf.fit_predict(lockmeanarray)

    # plt.scatter(lockmeanarray[:,0], lockmeanarray[:,1], c=y_pred)
    # # plt.show()
    # print(y_pred)

    # clfcenter = clf.cluster_centers_
    # for i in range(k):
    #     vexmin = math.sqrt((clfcenter[i][1]-min(y))**2+(clfcenter[i][0]-min(x))**2)
    #     vexmax = math.sqrt((clfcenter[i][1]-max(y))**2+(clfcenter[i][0]-max(x))**2)
    #     # print(vexmin, vexmax)
    #     if vexmin >20 and vexmax>20:
    #         vex = math.sqrt((clfcenter[i][1]*1000-utmloc_0[1])**2+(clfcenter[i][0]*1000-utmloc_0[0])**2)
    #         print(clfcenter[i], vex, vexmin, vexmax)

    # from sklearn.metrics import calinski_harabaz_score
    # print(calinski_harabaz_score(lockmeanarray, y_pred))

    # print(zi[1][0])
    # zmax =[]
    # for zz in zi:
    #     print(zz.type)
    #     if not(math.isnan(zz[0])):
    #         zmax.append(zz)
    # #     break
    # print(zmax)
    # print(np.amax(np.array(zmax)))



        

