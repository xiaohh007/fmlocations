# -*- coding:utf-8 -*-
import rssiclean
import numpy as np 
import pandas as pd 
from pandas import Series
import connmysql 
import math
from scipy.optimize import curve_fit
import bd09towgs84 as projtrans
# import matplotlib.pyplot as plt
from scipy.interpolate import griddata
# from mpl_toolkits.mplot3d  import Axes3D
# import scipy.signal as signal

def get_predvex(starttime, endtime):
    fmdatas = ['93.4','94','94.7','91.4','99','87.9','89.9','107.7']  #['87.9', '93.4', '91.4', '89.9', '107.7']
    x_vex = 0
    y_vex = 0
    lenfm = 0
    for fmdata in fmdatas:
        try:
            result = connmysql.get_fmdata(fmdata, starttime, endtime)
            
            data_clean, deviceids = rssiclean.get_rssidata_c(result,dbmax=-40, dbmin=-95)
            
            x = []
            y = []
            z = []
            utmloc_0 =[]
            for data in data_clean:
                if data['lon'] is not None and float(data['lon'])>100:
                    wgsloc = projtrans.bd09_to_wgs84(float(data['lon']), float(data['lat']))
                    utmloc = projtrans.wgs2utm(wgsloc[0], wgsloc[1])
                    data['lon'],data['lat'] = utmloc[0], utmloc[1]
                    x.append(utmloc[0]/1000)
                    y.append(utmloc[1]/1000)
                    z.append(data['db'])
                if data['fmlon'] is not None and float(data['fmlon'])>100:
                    wgsloc_0 = projtrans.bd09_to_wgs84(float(data['fmlon']), float(data['fmlat']))            
                    utmloc_0 = projtrans.wgs2utm(wgsloc_0[0], wgsloc_0[1])           
                    data['fmlon'],data['fmlat'] = utmloc_0[0], utmloc_0[1]
                
            
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

            # print(utmloc_0)
            # print("X的差值：",max(x)-min(x))
            # print("Y的差值：",max(y)-min(y))
            # print("Z的max：",max(z))

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
                        # print(locx, locy)
                        # print(zi[locy][locx])
                        if locx>50 and locy>50 and locx<len(xxi)-50 and locy<len(yyi)-50:
                            if abs(zi[locy][locx] - max(z))<5 or zi[locy][locx] > max(z):
                                locpreds.append([min(x)+locx*xinternal, min(y)+locy*yinternal])
                        break    
                pi += 1
            if len(locpreds) > 0:
                locpred = np.array(list(set([tuple(t) for t in locpreds])))
                locpx =0
                locpy =0
                count = 0

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
                    
                    # print(math.sqrt((locpy*1000-utmloc_0[1])**2+(locpx*1000-utmloc_0[0])**2))
                # print("1",x_vex,y_vex,locpx - utmloc_0[0]/1000,(locpy - utmloc_0[1]/1000))
                if locpx > 300:
                    x_vex += (locpx - utmloc_0[0]/1000)
                    y_vex += (locpy - utmloc_0[1]/1000)
                    lenfm += 1
        except:
            pass
    #     print("+",x_vex,y_vex)
    # print("vex:" ,x_vex, y_vex, lenfm)
    if lenfm > 0:
        x_vex = x_vex / lenfm
        y_vex = y_vex / lenfm
    # print("vex", x_vex,y_vex)
    return [x_vex, y_vex]

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

