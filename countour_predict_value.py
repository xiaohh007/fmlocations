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
import countor_predvex_opt as cpo
import getlinloc

def pred_location(fm, starttime, endtime):
    
    try:
        result = connmysql.get_fmdata(fm, starttime , endtime)
        data_clean, deviceids = rssiclean.get_rssidata_c(result)
        xy_vex = cpo.get_predvex(starttime , endtime)
        x = []
        y = []
        z = []
        utmloc_0 =[]
        locpx = 0
        locpy = 0
        points=[]
        px = []
        py = []
        typenum = 0


        
        for data in data_clean:
            # print(data['lon'])
            if data['lon'] is not None and float(data['lon'])>100:
                wgsloc = projtrans.bd09_to_wgs84(float(data['lon']), float(data['lat']))       
                utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
                data['lon'],data['lat'] = utmloc[0], utmloc[1]
                x.append(utmloc[0]/1000)
                y.append(utmloc[1]/1000)
                z.append(data['db'])
                # print("1")
                # print(data)
            try:
                if float(data['fmlon'])>100:
                    wgsloc_0 = projtrans.bd09_to_wgs84(float(data['fmlon']), float(data['fmlat']))
                    utmloc_0 = projtrans.wgs2utm(wgsloc_0[0], wgsloc_0[1])       
                    data['fmlon'],data['fmlat'] = utmloc_0[0], utmloc_0[1]
            except:
                pass
            
        # print(utmloc_0)
        # print(z)
        # print(x)
        # print(y)



        for i in range(len(x)):
            point=[]
            point.append(x[i])
            px.append(x[i])
            point.append(y[i])
            py.append(y[i])   
            points.append(point)
        points=np.array(points)

        # print("X的差值：",max(x)-min(x))
        # print("Y的差值：",max(y)-min(y))
        # print("Z的max：",max(z))
        if len(z) == 1:
            locpx, locpy = getlinloc.get1point(x[0], y[0])
            typenum = 5
            # print(locpx, locpy)
        elif len(z) == 2:
            locpx, locpy = getlinloc.get2point(points,z)
            typenum = 4
            # print(locpx, locpy)
            # if len(utmloc_0)>0:
            #     print(utmloc_0)
            #     print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
        elif len(z)>2 and len(z) < 4:
            zminindex = z.index(min(z))
            zmaxindex = z.index(max(z))
            pnearx, pneary = getlinloc.getlineloc(points[zminindex], points[zmaxindex])
            # print(pnearx, pneary)
            # print(points[zmaxindex][0], points[zmaxindex][1])
            locpx = (points[zmaxindex][0] + pnearx)/2
            locpy = (points[zmaxindex][1] + pneary)/2
            typenum = 4
            # print(locpx, locpy)
            # if len(utmloc_0)>0:
            #     print(utmloc_0)
            #     print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
        else:
            
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

            # zminindex = z.index(min(z))
            # zmaxindex = z.index(max(z))
            # lineparam = cj.IsCircle(points[zminindex], points[zmaxindex],min(x),max(x), xxi.tolist(), yyi.tolist(), zi)

            # if len(z)<8 and max(z)>-45 and max(z)<-40:
            #     # print(max(z))
            #     zindex = z.index(max(z))
            #     locpx, locpy = x[zindex], y[zindex]
            #     print(locpx,locpy)
            #     if len(utmloc_0)>0:
            #         print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
            # elif len(z)<7:
            #     # print(max(z))
            #     zindex = z.index(max(z))
            #     print(x[zindex], y[zindex])
            #     if len(utmloc_0)>0:
            #         print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
            # else:

            locpreds = []
            # zpred = []
            pi=0
            while pi < len(px):
                
                locx = int((px[pi] - min(x)) //xinternal)
                locy = int((py[pi]- min(y)) //yinternal)

                # print(locx,locy)
                # temp = 0
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
                        # mx, my = min(x)+locx*xinternal, min(y)+locy*yinternal
                        # print(min(x), min(y))
                        # print(zi[locy][locx])
                        if locx>50 and locy>50 and locx<len(xxi)-50 and locy<len(yyi)-50:
                            if abs(zi[locy][locx] - max(z))<5 or zi[locy][locx] > max(z):
                                locpreds.append([min(x)+locx*xinternal, min(y)+locy*yinternal])
                        break       
                pi += 1


            if len(locpreds)>0: #and len(z)>=6
                locpred = np.array(list(set([tuple(t) for t in locpreds])))
                locpx =0
                locpy =0
                count = 0
                # for locp in locpreds:
                #     vexp = math.sqrt((locp[1]*1000-utmloc_0[1])**2+(locp[0]*1000-utmloc_0[0])**2)
                #     print(locp, vexp)

                # print("------------------")
                # resdata = []

                for locp in locpred:
                    count = 0
                    for locps in locpreds:
                        # print((np.array(locp)==np.array(locps)).all())
                        if (np.array(locp)==np.array(locps)).all():
                            count += 1
                    # print(locp, count)
                    locpx += locp[0]*count
                    locpy += locp[1]*count
                if len(locpreds)>0:
                    locpx = locpx / len(locpreds)
                    locpy = locpy / len(locpreds)
                # print("0",locpx, locpy)
                # print(xy_vex)
                locpx -= xy_vex[0]
                locpy -= xy_vex[1]
                typenum = 1
                # print("1",locpx, locpy)
                # if len(utmloc_0)>0:
                #     print(utmloc_0)
                #     print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
            else: 
                    # print(locpx, locpy)
                    # print(math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))

                # print(locpx, locpy)
                # if len(utmloc_0)>0:
                #     print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))

                # print(xy_vex)
                zminindex = z.index(min(z))
                zmaxindex = z.index(max(z))
                pnearx, pneary = getlinloc.getlineloc(points[zminindex], points[zmaxindex])
                # print(pnearx, pneary)
                # print(points[zmaxindex][0], points[zmaxindex][1])
                locpx = (points[zmaxindex][0] + pnearx)/2
                locpy = (points[zmaxindex][1] + pneary)/2
                typenum = 2
                # print(locpx, locpy)
                # if len(utmloc_0)>0:
                #     print('距离差', math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
                
                # if max(z)>-45 :#and max(z)<-40
                #     # print(max(z))
                #     zindex = z.index(max(z))
                #     locpx, locpy = x[zindex], y[zindex]
                #     typenum = 2
                #     print(locpx,locpy)
                #     if len(utmloc_0)>0:
                #         print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
                # else:
                #     # print(max(z))
                #     zindex = z.index(max(z))
                #     print(x[zindex], y[zindex])
                #     if len(utmloc_0)>0:
                #         print('距离差', math.sqrt((y[zindex]*1000-utmloc_0[1])**2+(x[zindex]*1000-utmloc_0[0])**2))
                # else:
                
            # xx = np.linspace(lineparam[1] ,lineparam[3] ,10000)
            # yy = np.float(lineparam[0])*(xx-np.float(lineparam[1]))+ np.float(lineparam[2])
            # plt.plot(xx, yy, color='red')
            
            plt.contourf(xi,yi,zi,8,alpha=1,cmap=plt.cm.hsv)#画上颜色
            c = plt.contour(xi,yi,zi,[0,10]) #等高线绘制
            plt.plot(px,py,'ro')

            plt.plot(utmloc_0[0]/1000,utmloc_0[1]/1000,'yo')
            # 线条标注的绘制
            plt.clabel(c,inline=True,fontsize=10)
            # plt.show()
            
            fig = plt.figure()
            ax = plt.axes(projection='3d')
            ax.contour3D(xi, yi, zi, 50, cmap='CMRmap')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')
            #调整观察角度和方位角。这里将俯仰角设为60度，把方位角调整为35度
            ax.view_init(60, 35)
            plt.show()

        # plt.plot(px,py,'ro')
        # plt.plot(utmloc_0[0]/1000,utmloc_0[1]/1000,'yo')
        # plt.plot(locpx, locpy, "r+")
        # plt.show()

        wgs = projtrans.utm2wgs(locpx*1000, locpy*1000)
        bd = projtrans.wgs84_to_bd09(wgs[0], wgs[1])
        return [fm, bd[0], bd[1], deviceids,typenum]
    except:
        return [fm, None, None, deviceids, 0]

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



        

