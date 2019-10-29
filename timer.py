import datetime

import schedule
from geopy.distance import geodesic
from numba import none
from numpy import double

import countour_predict_value as cpv
from MysqlHelp import DB




global endtime
global comparelist
global coding
global radiovaluelists
radiovaluelists = []
comparelist = []


def five_minutes():
    endtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    starttime = (datetime.datetime.now()+datetime.timedelta(hours= -3)).strftime("%Y-%m-%d %H:%M:%S")
    print(starttime)
    # 查询在5分钟内,record表中新增的频率信息
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("SELECT distinct frequency FROM fm_t_scan_record where upload_time BETWEEN date_add(now(), interval - 5 minute) and now() ")
        frequencylist = db.fetchall()
        print(frequencylist)
    # 查询fmlocation表中,该频率是否存在
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("SELECT distinct frequency FROM fm_t_fmlocation ")
        codingfrequencydict = db.fetchall()
        codingfrequencylist = []


    # 遍历fmlocation表中存在的频率信息,获取每个频率的值
    for codingfrequency in codingfrequencydict:
        str_codingfrequency = list(codingfrequency.values())
        out = str(str_codingfrequency).replace('[','').replace(']','')
        codingfrequencylist.append(out)
    print(codingfrequencylist)

    # 遍历record表中的频率信息,获取每个频率的值
    for frequency in frequencylist:
        str_frequency = list(frequency.values())
        out = str(str_frequency).replace('[','').replace(']','')
        print(out)
        # 执行定位算法,获取定位的频率的定位lng(经度)lat(纬度)关联的设备,以及定位级别
        result = cpv.pred_location( out , starttime, endtime)
        result_frequency = result[0]
        result_lng = result[1]
        result_lat = result[2]
        result_accuratetype = str(result[4])

        # 查询radiolist表中各频率的详细的数据
        radiolists = query_radiolist(out)
        print("radiolists++++++++++++++",radiolists)

        print(result_accuratetype)
        result_facility_list = ",".join(result[3])
        serialnumber = 1
        print(result_lng)
        print(result_lat)
        print(type(result_lng))
        print(type(result_lat))
        print(frequency)

        # 判断经纬度是否在上海区域内
        if result_lat is not None and 30.0 <= result_lat <= 32.0:

            if result_lng is not None and result_lng > 100.0:

                # 判断该频率是存在于fmlocation表中
                if out in codingfrequencylist:
                    # 判断radiolist表中是否存在该频率并且未被取缔
                    print("len(radiolists)++++++++++++++",len(radiolists))
                    if len(radiolists) > 0:
                        for radiolist in radiolists:
                            # 存在该频率且未被取缔,将定位算法的数据与本表中的数据一一对比
                            print("radiolist+++++++++++++++++++++++",radiolist)
                            radio_lng = radiolist[3]
                            radio_lat = radiolist[4]

                            radio_fmcoding = radiolist[2]

                            coding = int(radio_fmcoding[-1])
                            distance_fm = error_range(radio_lng,radio_lat,result_lng,result_lat)

                            if distance_fm <20000:
                                # 定义数组compare,存放比较的范围状态,在范围内记为A,在范围外记为B,添加到数组中

                                comparelist.append("A")
                            else:
                                comparelist.append("B")

                        # 判断数组中是否有在范围内的数据,如果有新增数据更新信息,但fmcoding取radiolist中的fmcoding,
                        # 如果数组中都在范围外,则新增数据,fmcoding新建.
                        if "A" in comparelist:
                            with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                                db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                                            .format(endtime,result_frequency,result_lng,result_lat,radio_fmcoding,result_facility_list,result_accuratetype))
                        else:
                            fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                            fmcoding = fmcoding+'_'+str(coding + 1)
                            with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                                db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                                    .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))

                    else:

                        print("频率已取缔,新增数据!")
                        fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                        fmcoding = fmcoding+'_'+str(serialnumber)
                        with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                            db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                                       .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))

                else:
                    fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                    fmcoding = fmcoding+'_'+str(serialnumber)
                    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                        db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                            .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))

            else:
                print("数据计算有误,不保存数据")
                continue


        else:
            print("数据计算有误,不保存数据")
            continue

def query_radiolist(out):
    global radiovaluelist
    print('query_radiolist++++++++++++++++',out)
    radiovaluelist = []
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("select frequency,create_time,fmcoding,lng ,lat,ban_time FROM fm_t_radiolist WHERE frequency='{}' and ban_time is NULL order by id desc".format(float(out)))
        radiolist = db.fetchall()

    for radio in radiolist:
        print(radio)
        radiovaluelist = list(radio.values())

        radiovaluelists.append(radiovaluelist)

    return radiovaluelists




def error_range(radio_lng,radio_lat,result_lng,result_lat):
    distance_fm = geodesic((radio_lat,radio_lng), (result_lat,result_lng)).m
    return float(distance_fm)

if __name__ == '__main__':





    # schedule.every(5).seconds.do(job1)
    schedule.every(300).seconds.do(five_minutes)
    # schedule.every(50).seconds.do(thirty_minutes)
    # schedule.every(500).seconds.do(one_day)

    while True:
        schedule.run_pending()