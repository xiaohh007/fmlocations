import datetime

from numba import none

from MysqlHelp import DB


out = '107.2'
with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
    db.execute("select frequency,create_time,fmcoding,lng ,lat,ban_time FROM fm_t_radiolist WHERE frequency='{}'".format(out))
    radiolist = db.fetchall()

    print("radiolist++++++++++++++",radiolist)

    for radio in radiolist:
        print("radio++++++++++++",radio)
        radiovaluelist = list(radio.values())
        print(radiovaluelist)
        # print(radiovalue)
        if radiovaluelist[3] is not None and radiovaluelist[4] is not None:
            radio_lng = float(radiovaluelist[3])
            radio_lat = float(radiovaluelist[4])
            radio_createtime = radiovaluelist[1]
            radio_fmcoding = radiovaluelist[2]
            radio_bantime = radiovaluelist[5]
            print(radio_lng)
            print(radio_lat)
            print(radio_createtime)
            print(radio_fmcoding)
            print(radio_bantime)
#
# from geopy.distance import geodesic
#
# print(geodesic((31.30169546322556,121.38089409658731), (30.96444862415061,121.15025151332885)).m) #计算两个坐标直线距离
# print(geodesic((31.30169546322556,121.38089409658731), (30.96444862415061,121.15025151332885)).km) #计算两个坐标直线距离


# coding = 'asdfl;lk;kk'
# print(coding[-1])