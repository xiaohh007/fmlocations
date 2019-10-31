import copy
import datetime

import schedule
from geopy.distance import geodesic
from numba import none
from numpy import double

import countour_predict_value as cpv
from MysqlHelp import DB










radiovaluelists = []

def five_minutes():
    global endtime
    global coding
    global comparelist
    comparelist = []
    comparelocationlist = []


    endtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    starttime = (datetime.datetime.now()+datetime.timedelta(hours= -12)).strftime("%Y-%m-%d %H:%M:%S")
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
        radiolists.clear()


        print(result_accuratetype)
        result_facility_list = ",".join(result[3])
        serialnumber = 1
        print(result_lng)
        print(result_lat)
        print(type(result_lng))
        print(type(result_lat))
        print(frequency)

        radio_lists = copy.deepcopy(radiolists)

        # 判断经纬度是否在上海区域内
        if result_lat is not None and 30.0 <= result_lat <= 32.0:

            if result_lng is not None and result_lng > 100.0:

                # 判断该频率是存在于fmlocation表中
                if out in codingfrequencylist:
                    # 判断radiolist表中是否存在该频率并且未被取缔

                    if len(radiolists) > 0:

                        for radio_list in radio_lists:
                            # 存在该频率且未被取缔,将定位算法的数据与本表中的数据一一对比
                            print("radio_list+++++++++++++++",radio_list)

                            radio_lng = radio_list[2]
                            radio_lat = radio_list[3]

                            radio_fmcoding = radio_list[1]

                            coding = int(radio_fmcoding[-1])
                            distance_fm = error_range(radio_lng,radio_lat,result_lng,result_lat)


                            if distance_fm <20000:
                                # 定义数组compare,存放比较的范围状态,在范围内记为A,在范围外记为B,添加到数组中

                                comparelist.append({'A':radio_fmcoding})
                            else:
                                comparelist.append({'B':radio_fmcoding})



                        # 判断数组中是否有在范围内的数据,如果有新增数据更新信息,但fmcoding取radiolist中的fmcoding,
                        # 如果数组中都在范围外,则新增数据,fmcoding新建.
                        compare_list = copy.deepcopy(comparelist)
                        comparelist.clear()
                        print("compare_list++++++++++++++++++++++++++",compare_list)

                        for compare in compare_list:
                            compare_key = []
                            compare_key.append(list(compare.keys()))

                            if "A" in compare_key:
                                compare_code = list(compare.values())
                                compare_coding = str(compare_code).replace('[','').replace(']','').replace('\'','')
                                print(compare_coding)
                                with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                                    db.execute("update fm_t_fmlocation set time='{}',lng='{}',lat='{}',equipmentschedule='{}',positioning_level='{}' where fmcoding = '{}' AND positioning_level < '{}'"
                                                .format(endtime,result_lng,result_lat,result_facility_list,result_accuratetype,compare_coding,result_accuratetype))
                                continue
                        else:
                            fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                            fmcoding = fmcoding+'_'+str(coding + 1)
                            with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
                                db.execute("INSERT into fm_t_fmlocation (id,time,size,frequency,lng,lat,fmcoding,equipmentschedule,positioning_level) VALUES(null,'{}',5,'{}','{}','{}','{}','{}','{}')"
                                    .format(endtime,result_frequency,result_lng,result_lat,fmcoding,result_facility_list,result_accuratetype))





                    else:
                        # 判断fmlocation表中是否存在范围内的数据,如果有则不新增,没有则新增
                        # 查询fmlocation表中对应的频率的详细信息
                        fm_location = query_fmlocationlist(out)
                        print('fm_location++++++++++++++++++',fm_location)
                        for fmlocation in fm_location:
                            print('fmlocation++++++++++++++++++',fmlocation)
                            location_coding = fmlocation[1]
                            location_lng = fmlocation[2]
                            location_lat = fmlocation[3]
                            distance_location = error_range(location_lng,location_lat,result_lng,result_lat)

                            if distance_location <20000:
                                # 定义数组compare,存放比较的范围状态,在范围内记为A,在范围外记为B,添加到数组中

                                comparelocationlist.append({'A':location_coding})
                            else:
                                comparelocationlist.append({'B':location_coding})

                        # 一一比对误差范围,只要有一条数据的误差范围小于20km,则该频率发射源是一个已存在的,否则则是一个新的发射源
                        comparelocation_list = copy.deepcopy(comparelocationlist)
                        print('comparelocationlist++++++++++++++++++++++++++++',comparelocationlist)
                        comparelocationlist.clear()
                        print('comparelocationlist2++++++++++++++++++++++++++++',comparelocationlist)


                        print('comparelocation_list++++++++++',comparelocation_list)


                        comparelocationkey = []
                        for compareloca in comparelocation_list:

                            for comparelocakey in list(compareloca.keys()):

                                comparelocationkey.append(comparelocakey)


                        print("comparelocationkey+++++++++++++++++++",comparelocationkey)


                        if 'A' in comparelocationkey:
                                # comparelocation_code = comparelocation.values()
                                # comparelocation_coding = str(comparelocation_code).replace('[','').replace(']','').replace('\'','')
                                print("该频率已存在,范围在已知的频率范围内,不对数据库进行操作")

                        else:
                            codings = int(location_coding[-1])
                            print("该频率已存在,但范围不在已知频率的范围之内,应新增一条记录")
                            fmcoding = str(result_frequency+"_"+str(endtime).replace('-','').replace(':','').replace(' ',''))
                            fmcoding = fmcoding+'_'+str(codings+1)
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

    radiovaluelist = []
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("select frequency,fmcoding,lng ,lat FROM fm_t_radiolist WHERE frequency='{}' and ban_time is NULL order by create_time desc".format(float(out)))
        radiolist = db.fetchall()

    for radio in radiolist:

        radiovaluelist = list(radio.values())

        radiovaluelists.append(radiovaluelist)

    return radiovaluelists

def query_fmlocationlist(out):

    locationvaluelist = []
    print("query_fmlocationlist(out)+++++++++",out)
    with DB(host='47.92.33.19',user='root',passwd='1qazxsw2',db='database_fm') as db:
        db.execute("select frequency,fmcoding,lng ,lat FROM fm_t_fmlocation WHERE frequency='{}' ".format(float(out)))
        locationlist = db.fetchall()

    for location in locationlist:

        valuelist = list(location.values())

        locationvaluelist.append(valuelist)

    locationvaluelists = copy.deepcopy(locationvaluelist)

    locationvaluelist.clear()
    print()
    return locationvaluelists


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