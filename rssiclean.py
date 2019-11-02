# -*- coding:utf-8 -*-
# import pandas as pd 
import numpy as np 
import GaussFB
import KalmanFilter



def get_rssidata_c(result, dbmin=-95, dbmax=-20):

    indexs = []
    for index, row in result.iterrows():
        if row['lon'] is not None and float(row['lon'])<100 and float(row['lat'])<20:
            indexs.append(index)
    result = result.drop(index=indexs)
    # print(result)
    indexdb = []
    for index, row in result.iterrows():
        if float(row['db'])>dbmax or float(row['db'])<dbmin:
            indexdb.append(index)
    result = result.drop(index=indexdb)

    data_clbyr = []
    data_gauss = []
    result_gbydids = result.groupby('deviceid')
    # print(len(result))
    # print(len(result_gbydids))
    
    # #利用高斯分布对单个接收站按时间序列剔除异常值
    # for index, result_deviceid in result_gbydids:
    #     if len(result_deviceid)>2:
    #         for data in result_deviceid['db'].values.tolist():
    #             data_gauss.append(float(data))
    #         usigma = GaussFB.Gaussfb(data_gauss)
            
    #         for key, row in result_deviceid.iterrows():
    #             if float(row['db'])<usigma[0]+1*usigma[1] and float(row['db'])>usigma[0]-1*usigma[1]:
    #                 data_clbyr.append(row)
    #     else:
    #         for key, row in result_deviceid.iterrows():
    #             data_clbyr.append(row)
    # #按接收站计算rssi平均值
    # result_gbydids = []
    # result_gbydids = pd.DataFrame(data_clbyr).groupby('deviceid')
    # data_clbyr_m = []
    # for index, result_deviceid in result_gbydids:
    #     datadb = []
    #     for data in result_deviceid['db'].values.tolist():
    #         datadb.append(float(data))
    #     datadb_mean = np.mean(datadb)
    #     for key,row in result_deviceid.iterrows():
    #         # print(row)
    #         row['db'] = datadb_mean
    #         # print('datamean:',datadb_mean)
    #         data_clbyr_m.append(row)
    #         break

    # 利用卡尔曼滤波取db
    deviceids = []
    data_clbyr_m = []
    for index, result_deviceid in result_gbydids:
        if len(result_deviceid)>2:
            data_gauss = []
            for data in result_deviceid['db'].values.tolist():
                data_gauss.append(float(data))
                
            if max(data_gauss)-min(data_gauss)<=20:
                usigma = GaussFB.Gaussfb(data_gauss)
                data_clbyr = []
                for key, row in result_deviceid.iterrows():
                    if float(row['db'])<=usigma[0]+3*usigma[1] and float(row['db'])>=usigma[0]-3*usigma[1]:
                        data_clbyr.append(float(row['db']))
                realvalue = KalmanFilter.get_realvalue(data_clbyr)
                for key, row in result_deviceid.iterrows():
                    row['db'] = realvalue
                    data_clbyr_m.append(row)
                    deviceids.append(row['deviceid'])
                    break
        # else:
        #     data_gauss = []
        #     for data in result_deviceid['db'].values.tolist():
        #         data_gauss.append(float(data))
        #         meanvalue = np.mean(data_gauss)
        #     for key, row in result_deviceid.iterrows():
        #         row['db'] = realvalue
        #         data_clbyr_m.append(row)
        #         break


    # print(data_clbyr_m)
    return data_clbyr_m, deviceids

# result = connmysql.get_fmdata()
# d = get_rssidata_c(result)
# print(d)
# print(len(data_clbyr_m))



